from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import ResearchLog
from backend.app.database.session import get_db

router = APIRouter(prefix="/api/logs", tags=["Audit & Diagnostic Logs"])


@router.get("")
async def list_logs(
    severity: Optional[str] = None,
    component: Optional[str] = None,
    candidate_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lists structured audit and diagnostic events."""
    query = select(ResearchLog).order_by(desc(ResearchLog.timestamp)).offset(offset).limit(limit)

    if severity:
        query = query.where(ResearchLog.severity == severity.upper())
    if component:
        query = query.where(ResearchLog.component == component.upper())
    if candidate_id:
        query = query.where(ResearchLog.candidate_id == candidate_id)
    if simulation_id:
        query = query.where(ResearchLog.simulation_id == simulation_id)

    res = await db.execute(query)
    logs = res.scalars().all()

    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "severity": l.severity,
            "component": l.component,
            "event": l.event,
            "candidate_id": l.candidate_id,
            "simulation_id": l.simulation_id,
            "message": l.message,
            "metadata": l.diagnostic_metadata
        }
        for l in logs
    ]


@router.get("/{log_id}")
async def get_log_detail(log_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves deep diagnostic metadata for debugging modal."""
    stmt = select(ResearchLog).where(ResearchLog.id == log_id)
    res = await db.execute(stmt)
    l = res.scalar_one_or_none()

    if not l:
        raise HTTPException(status_code=404, detail="Log entry not found")

    return {
        "id": l.id,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        "severity": l.severity,
        "component": l.component,
        "event": l.event,
        "candidate_id": l.candidate_id,
        "simulation_id": l.simulation_id,
        "message": l.message,
        "metadata": l.diagnostic_metadata
    }
