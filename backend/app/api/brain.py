import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.brain.authentication import brain_auth
from backend.app.config import settings
from backend.app.core.security import vault
from backend.app.database.models import BrainConnection, BrainSession
from backend.app.database.session import get_db

router = APIRouter(prefix="/api/brain", tags=["WorldQuant BRAIN Connection"])


class BrainAuthRequest(BaseModel):
    email: str
    password: str
    environment: str = Field(default="PROD")


class BrainHealthResponse(BaseModel):
    status: str
    brain_api_url: str
    environment: str
    connected: bool
    email: Optional[str] = None
    last_tested: Optional[str] = None


@router.get("/health", response_model=BrainHealthResponse)
async def get_brain_health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint for WorldQuant BRAIN API connectivity."""
    stmt = select(BrainConnection).where(BrainConnection.is_active == True)
    res = await db.execute(stmt)
    conn = res.scalars().first()

    connected = bool(conn and conn.status == "CONNECTED")
    last_tested = conn.last_tested_at.isoformat() if (conn and conn.last_tested_at) else None

    return BrainHealthResponse(
        status="ONLINE" if connected else "NOT_CONNECTED",
        brain_api_url=settings.BRAIN_API_BASE_URL,
        environment=conn.environment if conn else "PROD",
        connected=connected,
        email=conn.email if conn else None,
        last_tested=last_tested
    )


@router.post("/auth/test")
async def test_brain_authentication(req: BrainAuthRequest):
    """
    Tests credentials against WorldQuant BRAIN API without saving session.
    Returns safe diagnostic status.
    """
    result = await brain_auth.authenticate(req.email, req.password, req.environment)
    return {
        "status": result["status"],
        "status_code": result["status_code"],
        "latency_ms": result.get("latency_ms", 0),
        "message": "Authentication successful" if result["status"] == "BRAIN_AUTH_SUCCESS" else result.get("error_message", "Authentication failed")
    }


@router.post("/connect")
async def connect_brain_account(req: BrainAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticates and securely stores encrypted credentials and session for WorldQuant BRAIN.
    """
    result = await brain_auth.authenticate(req.email, req.password, req.environment)
    
    if result["status"] != "BRAIN_AUTH_SUCCESS":
        return {
            "success": False,
            "status": result["status"],
            "message": result.get("error_message", "Authentication failed.")
        }

    # Deactivate existing active connections first
    active_stmt = select(BrainConnection).where(BrainConnection.is_active == True)
    active_res = await db.execute(active_stmt)
    for old_conn in active_res.scalars().all():
        old_conn.is_active = False
        old_conn.status = "DISCONNECTED"

    # Encrypt password & session cookies
    encrypted_pw = vault.encrypt(req.password)
    encrypted_cookie = vault.encrypt(json.dumps(result.get("cookies", {})))

    # Check for existing connection by email
    stmt = select(BrainConnection).where(BrainConnection.email == req.email)
    res = await db.execute(stmt)
    conn = res.scalar_one_or_none()

    if not conn:
        conn = BrainConnection(
            email=req.email,
            encrypted_password=encrypted_pw,
            environment=req.environment,
            status="CONNECTED",
            is_active=True,
            last_tested_at=datetime.now(timezone.utc),
            last_status_code="200"
        )
        db.add(conn)
        await db.flush()
    else:
        conn.encrypted_password = encrypted_pw
        conn.environment = req.environment
        conn.status = "CONNECTED"
        conn.is_active = True
        conn.last_tested_at = datetime.now(timezone.utc)
        conn.last_status_code = "200"

    # Save session
    sess = BrainSession(
        connection_id=conn.id,
        encrypted_session_cookie=encrypted_cookie,
        is_valid=True
    )
    db.add(sess)
    await db.commit()

    return {
        "success": True,
        "status": "BRAIN_AUTH_SUCCESS",
        "connection_id": conn.id,
        "email": conn.email,
        "environment": conn.environment,
        "message": "WorldQuant BRAIN account connected successfully."
    }


@router.post("/disconnect")
async def disconnect_brain_account(db: AsyncSession = Depends(get_db)):
    """Disconnects and clears active BRAIN connection."""
    stmt = select(BrainConnection).where(BrainConnection.is_active == True)
    res = await db.execute(stmt)
    conn = res.scalars().first()

    if conn:
        conn.status = "DISCONNECTED"
        conn.is_active = False
        await db.commit()

    return {"success": True, "message": "BRAIN account disconnected."}
