from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.ai.key_manager import ai_key_manager
from backend.app.ai.provider import AnthropicProvider, GeminiProvider, OpenAIProvider
from backend.app.config import settings
from backend.app.core.logging import verde_logger
from backend.app.generation.family_info import RESEARCH_FAMILIES


class AIManager:
    """Orchestrates optional AI research assistance for hypothesis generation and failure diagnostics."""

    @staticmethod
    async def generate_hypotheses(
        provider_name: str,
        family_code: str,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generates research hypotheses using the configured AI provider, falling back to deterministic synthesis if offline."""
        p_name = provider_name.upper().strip()
        family = RESEARCH_FAMILIES.get(family_code, RESEARCH_FAMILIES["MOMENTUM"])
        fields = family.get("preferred_fields", ["close", "returns", "vwap"])

        # Fetch decrypted key
        api_key = await ai_key_manager.get_decrypted_key(session, p_name)

        if not api_key:
            verde_logger.log_event(
                event="AI_FALLBACK_ACTIVE",
                severity="INFO",
                component="AI_MANAGER",
                message=f"No active API key configured for {p_name}. Utilizing deterministic hypothesis engine."
            )
            # Deterministic quantitative fallback
            return [
                {
                    "title": f"Deterministic Hypothesis: {family['name']} Momentum Decay",
                    "rationale": f"Analyzes trend continuation in {family_code} factors using normalized cross-sectional rankings.",
                    "suggested_fields": fields[:3],
                    "suggested_operators": ["rank", "ts_mean", "group_neutralize"]
                },
                {
                    "title": f"Deterministic Hypothesis: {family['name']} Idiosyncratic Spreads",
                    "rationale": "Removes sector-wide drift by applying granular subindustry neutralization.",
                    "suggested_fields": fields[:2],
                    "suggested_operators": ["divide", "rank", "group_neutralize"]
                }
            ]

        # Call live provider
        try:
            if p_name == "OPENAI":
                provider = OpenAIProvider()
            elif p_name == "ANTHROPIC":
                provider = AnthropicProvider()
            elif p_name in ("GEMINI", "GOOGLE"):
                provider = GeminiProvider()
            else:
                provider = OpenAIProvider()

            return await provider.generate_hypotheses(api_key, family_code, fields)
        except Exception as e:
            verde_logger.log_event(
                event="AI_GENERATION_FAILED",
                severity="WARNING",
                component="AI_MANAGER",
                message=f"AI generation failed for {p_name}: {str(e)}"
            )
            return [
                {
                    "title": f"Robust Hypothesis: {family['name']} Relative Dynamics",
                    "rationale": f"Evaluates {family_code} dynamics with safe division and volatility normalizers.",
                    "suggested_fields": fields[:3],
                    "suggested_operators": ["rank", "ts_zscore", "group_neutralize"]
                }
            ]


ai_manager = AIManager()
