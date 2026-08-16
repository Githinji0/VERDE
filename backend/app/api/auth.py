from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import User
from backend.app.database.session import get_db

router = APIRouter(prefix="/api/auth", tags=["User Authentication"])


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


@router.get("/me")
async def get_current_user_status():
    """Returns local session status for research platform operator."""
    return {
        "authenticated": True,
        "username": "lead_quant",
        "email": "quant@verde.research",
        "role": "QUANT_RESEARCHER"
    }
