import pytest
from backend.app.brain.simulator import simulation_sandbox
from backend.app.brain.client import brain_client
from backend.app.brain.response_parser import response_parser


@pytest.mark.asyncio
async def test_simulation_sandbox_execution():
    expr = "rank(ts_decay_linear(volume, 10))"
    res = await brain_client.submit_simulation(
        expression=expr,
        environment="SIMULATION",
        family_code="MOMENTUM"
    )
    assert res["status"] == "COMPLETE"
    assert res["status_code"] == 200
    assert "data" in res
    
    parsed = response_parser.parse_simulation_response(res["data"])
    assert parsed["classification"] == "VALID_METRICS"
    assert parsed["portfolio_status"] == "VALID"
    assert parsed["metrics_status"] == "AVAILABLE"
    assert parsed["has_valid_metrics"] is True
    assert parsed["sharpe"] is not None
    assert parsed["fitness"] is not None
    assert parsed["turnover"] is not None
    assert parsed["margin_bps"] is not None
