import pytest
from backend.app.generation.preflight import preflight_engine


@pytest.mark.asyncio
async def test_preflight_syntax_validation():
    # Valid syntax
    valid, err = preflight_engine.validate_syntax("rank(close / ts_delay(close, 20))")
    assert valid is True
    assert err is None

    # Mismatched unclosed parenthesis
    valid, err = preflight_engine.validate_syntax("rank(close / ts_delay(close, 20)")
    assert valid is False
    assert "Unclosed" in err


@pytest.mark.asyncio
async def test_preflight_constant_signal_detection():
    # Dividing rolling mean by itself
    expr = "ts_mean(close, 20) / ts_mean(close, 20)"
    risk, warnings = preflight_engine.check_constant_signal_risk(expr)
    assert risk >= 0.9
    assert len(warnings) > 0


@pytest.mark.asyncio
async def test_preflight_temporal_incompatibility():
    # Slow moving capex with 5-day rolling mean
    expr = "ts_mean(capex, 5)"
    fields, ops = preflight_engine.extract_fields_and_operators(expr)
    score, issues = preflight_engine.check_temporal_compatibility(expr, fields, ops)
    assert score < 0.8
    assert len(issues) > 0


@pytest.mark.asyncio
async def test_preflight_valid_momentum_candidate():
    expr = "rank(close / ts_delay(close, 20) - 1)"
    res = await preflight_engine.run_preflight(expr, "MOMENTUM")
    assert res["decision"] == "PASS"
    assert res["reason"] == "PREFLIGHT_PASSED"
    assert res["constant_signal_risk"] < 0.2
