from typing import Any, Dict
from backend.app.ai.provider import AnthropicProvider, GeminiProvider, OpenAIProvider


async def validate_ai_api_key(provider_name: str, api_key: str) -> Dict[str, Any]:
    """Validates an API key against the specified AI provider endpoint."""
    p_name = provider_name.upper().strip()
    if p_name == "OPENAI":
        provider = OpenAIProvider()
        return await provider.validate_api_key(api_key)
    elif p_name == "ANTHROPIC":
        provider = AnthropicProvider()
        return await provider.validate_api_key(api_key)
    elif p_name in ("GEMINI", "GOOGLE"):
        provider = GeminiProvider()
        return await provider.validate_api_key(api_key)
    else:
        return {
            "status": "AI_PROVIDER_UNAVAILABLE",
            "status_code": 400,
            "message": f"Provider '{provider_name}' is not supported."
        }
