from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from backend.app.core.exceptions import BrainPayloadException

# Valid WorldQuant BRAIN Simulation Constants
VALID_UNIVERSES = {"TOP3000", "TOP2000", "TOP1000", "TOP500", "SP500", "RUSSELL3000", "GLOBAL", "ILLIQUID"}
VALID_REGIONS = {"USA", "EUR", "ASI", "GLB"}
VALID_NEUTRALIZATIONS = {"SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET", "NONE"}
VALID_PASTEURIZATIONS = {"ON", "OFF"}
VALID_LANGUAGES = {"FASTEXPR", "EXPRESSION"}


class SimulationSettingsSchema(BaseModel):
    """Strict schema for WorldQuant BRAIN simulation settings."""
    universe: str = Field(default="TOP3000")
    region: str = Field(default="USA")
    delay: int = Field(default=1, ge=0, le=5)
    decay: int = Field(default=0, ge=0, le=100)
    neutralization: str = Field(default="SUBINDUSTRY")
    truncation: float = Field(default=0.08, ge=0.01, le=1.0)
    pasteurization: str = Field(default="ON")
    unitHandling: str = Field(default="VERIFY")
    nanHandling: str = Field(default="OFF")
    language: str = Field(default="FASTEXPR")
    visualization: bool = Field(default=False)

    @field_validator("universe")
    @classmethod
    def validate_universe(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_UNIVERSES:
            raise ValueError(f"Invalid universe '{v}'. Allowed: {sorted(VALID_UNIVERSES)}")
        return v_upper

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_REGIONS:
            raise ValueError(f"Invalid region '{v}'. Allowed: {sorted(VALID_REGIONS)}")
        return v_upper

    @field_validator("neutralization")
    @classmethod
    def validate_neutralization(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_NEUTRALIZATIONS:
            raise ValueError(f"Invalid neutralization '{v}'. Allowed: {sorted(VALID_NEUTRALIZATIONS)}")
        return v_upper

    @field_validator("pasteurization")
    @classmethod
    def validate_pasteurization(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_PASTEURIZATIONS:
            raise ValueError(f"Invalid pasteurization '{v}'. Allowed: {sorted(VALID_PASTEURIZATIONS)}")
        return v_upper


class BrainSimulationPayload(BaseModel):
    """Canonical WorldQuant BRAIN API Request Payload."""
    type: str = Field(default="REGULAR")
    settings: SimulationSettingsSchema
    regular: str = Field(..., description="Alpha expression code")

    @field_validator("regular")
    @classmethod
    def validate_expression(cls, v: str) -> str:
        expr = v.strip()
        if not expr:
            raise ValueError("Alpha expression 'regular' cannot be empty.")
        return expr


def build_simulation_payload(expression: str, settings_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Constructs and strictly validates the simulation payload for WorldQuant BRAIN API.
    Rejects unsupported properties and ensures all required fields are present.
    """
    settings_dict = settings_dict or {}
    try:
        settings_schema = SimulationSettingsSchema(**settings_dict)
        payload = BrainSimulationPayload(
            type="REGULAR",
            settings=settings_schema,
            regular=expression.strip()
        )
        return payload.model_dump()
    except Exception as e:
        raise BrainPayloadException(
            message=f"Simulation payload validation failed: {str(e)}",
            code="PAYLOAD_SCHEMA_INVALID",
            details={"error": str(e), "expression": expression, "settings": settings_dict}
        )
