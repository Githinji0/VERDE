from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.ai.key_manager import ai_key_manager
from backend.app.ai.manager import ai_manager
from backend.app.ai.validators import validate_ai_api_key
from backend.app.config import settings
from backend.app.database.models import AIApiKeyMetadata, AIProvider
from backend.app.database.session import get_db

router = APIRouter(prefix="/api/ai", tags=["AI Lab & Key Management"])


class AIKeyValidationRequest(BaseModel):
    provider_name: str = Field(default="OPENAI")
    api_key: str


class AIHypothesisRequest(BaseModel):
    provider_name: str = Field(default="OPENAI")
    family_code: str = Field(default="MOMENTUM")


@router.get("/providers")
async def list_ai_providers(db: AsyncSession = Depends(get_db)):
    """Lists supported AI providers and their configuration status."""
    stmt = select(AIApiKeyMetadata)
    res = await db.execute(stmt)
    keys = {k.provider_name: k.key_hint for k in res.scalars().all()}

    providers = [
        {
            "name": "OPENAI",
            "display_name": "OpenAI (GPT-4o)",
            "has_key": "OPENAI" in keys,
            "key_hint": keys.get("OPENAI"),
            "status": "CONFIGURED" if "OPENAI" in keys else "NOT_CONFIGURED"
        },
        {
            "name": "ANTHROPIC",
            "display_name": "Anthropic (Claude 3.5 Sonnet)",
            "has_key": "ANTHROPIC" in keys,
            "key_hint": keys.get("ANTHROPIC"),
            "status": "CONFIGURED" if "ANTHROPIC" in keys else "NOT_CONFIGURED"
        },
        {
            "name": "GEMINI",
            "display_name": "Google Gemini (Gemini 1.5 Pro)",
            "has_key": "GEMINI" in keys,
            "key_hint": keys.get("GEMINI"),
            "status": "CONFIGURED" if "GEMINI" in keys else "NOT_CONFIGURED"
        }
    ]

    return {"providers": providers, "ai_globally_enabled": settings.AI_ENABLED}


@router.post("/validate-key")
async def validate_and_save_ai_key(req: AIKeyValidationRequest, db: AsyncSession = Depends(get_db)):
    """
    Validates external AI API key and securely encrypts & stores it.
    Never exposes raw key in response.
    """
    val_result = await validate_ai_api_key(req.provider_name, req.api_key)

    if val_result["status"] == "AI_KEY_VALID":
        record = await ai_key_manager.store_key(db, req.provider_name, req.api_key)
        return {
            "status": "AI_KEY_VALID",
            "provider": req.provider_name.upper(),
            "key_hint": record.key_hint,
            "message": "AI API key validated and securely stored."
        }
    else:
        return {
            "status": val_result["status"],
            "provider": req.provider_name.upper(),
            "message": val_result.get("message", "API key validation failed.")
        }


@router.post("/hypothesis")
async def generate_ai_hypothesis(req: AIHypothesisRequest, db: AsyncSession = Depends(get_db)):
    """Generates structured quantitative research hypotheses via AI assistant."""
    hypotheses = await ai_manager.generate_hypotheses(req.provider_name, req.family_code, db)
    return {"family_code": req.family_code, "provider": req.provider_name, "hypotheses": hypotheses}
