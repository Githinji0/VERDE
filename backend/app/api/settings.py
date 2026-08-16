from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.research.priority_engine import priority_engine

router = APIRouter(prefix="/api/settings", tags=["System Settings"])


class SettingsUpdateRequest(BaseModel):
    min_sharpe: float = Field(default=1.25, ge=0.5, le=5.0)
    min_fitness: float = Field(default=1.00, ge=0.2, le=5.0)
    max_turnover: float = Field(default=0.70, ge=0.01, le=1.0)
    min_margin_bps: float = Field(default=4.00, ge=0.0, le=100.0)
    proven_ratio: float = Field(default=0.70, ge=0.0, le=1.0)
    explored_ratio: float = Field(default=0.20, ge=0.0, le=1.0)
    novel_ratio: float = Field(default=0.10, ge=0.0, le=1.0)
    ai_enabled: bool = Field(default=False)
    brain_debug: bool = Field(default=False)


@router.get("")
async def get_system_settings():
    """Retrieves current configurable validation thresholds and project settings."""
    return {
        "validation_targets": {
            "min_sharpe": settings.MIN_SHARPE,
            "min_fitness": settings.MIN_FITNESS,
            "max_turnover": settings.MAX_TURNOVER,
            "min_margin_bps": settings.MIN_MARGIN_BPS,
            "near_miss_min_sharpe": settings.NEAR_MISS_MIN_SHARPE,
            "near_miss_max_sharpe": settings.NEAR_MISS_MAX_SHARPE,
            "near_miss_min_fitness": settings.NEAR_MISS_MIN_FITNESS,
            "near_miss_max_fitness": settings.NEAR_MISS_MAX_FITNESS
        },
        "priority_allocation": priority_engine.get_allocation_ratios(),
        "preflight_thresholds": {
            "min_valid_ratio": settings.PREFLIGHT_MIN_VALID_RATIO,
            "min_unique_values": settings.PREFLIGHT_MIN_UNIQUE_VALUES,
            "constant_tolerance": settings.PREFLIGHT_CONSTANT_TOLERANCE
        },
        "score_weights": {
            "sharpe": settings.WEIGHT_SHARPE,
            "fitness": settings.WEIGHT_FITNESS,
            "turnover": settings.WEIGHT_TURNOVER,
            "stability": settings.WEIGHT_STABILITY,
            "robustness": settings.WEIGHT_ROBUSTNESS,
            "diversity": settings.WEIGHT_DIVERSITY,
            "simplicity": settings.WEIGHT_SIMPLICITY
        },
        "flags": {
            "ai_enabled": settings.AI_ENABLED,
            "brain_debug": settings.BRAIN_DEBUG
        }
    }


@router.put("")
async def update_system_settings(req: SettingsUpdateRequest):
    """Updates configurable research targets and priority ratios."""
    settings.MIN_SHARPE = req.min_sharpe
    settings.MIN_FITNESS = req.min_fitness
    settings.MAX_TURNOVER = req.max_turnover
    settings.MIN_MARGIN_BPS = req.min_margin_bps
    settings.AI_ENABLED = req.ai_enabled
    settings.BRAIN_DEBUG = req.brain_debug

    priority_engine.set_allocation_ratios(req.proven_ratio, req.explored_ratio, req.novel_ratio)

    return {
        "success": True,
        "message": "Settings updated successfully."
    }
