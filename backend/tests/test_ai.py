import pytest
from backend.app.ai.key_manager import create_key_hint
from backend.app.ai.manager import ai_manager
from backend.app.database.session import AsyncSessionFactory, init_db


def test_ai_key_hint_security():
    assert create_key_hint("sk-proj-12345678abcdef") == "sk-...cdef"
    assert create_key_hint("short") == "••••••••"


@pytest.mark.asyncio
async def test_ai_deterministic_fallback_when_unconfigured():
    await init_db()
    async with AsyncSessionFactory() as session:
        # With no key configured, should gracefully return deterministic quantitative hypotheses
        hyps = await ai_manager.generate_hypotheses("OPENAI", "MOMENTUM", session)
        assert len(hyps) > 0
        assert "Momentum" in hyps[0]["title"]
        assert len(hyps[0]["suggested_fields"]) > 0
