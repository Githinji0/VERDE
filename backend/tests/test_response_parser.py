import pytest
from backend.app.brain.response_parser import response_parser


def test_parse_valid_simulation_response():
    data = {
        "stats": {
            "sharpe": 1.45,
            "fitness": 1.12,
            "turnover": 0.35,
            "margin": 6.2,
            "returns": 0.18,
            "drawdown": 0.08,
            "longCount": 150,
            "shortCount": 145
        },
        "records": [{"pnl": 100}]
    }

    res = response_parser.parse_simulation_response(data)
    assert res["classification"] == "VALID_METRICS"
    assert res["portfolio_status"] == "VALID"
    assert res["metrics_status"] == "AVAILABLE"
    assert res["has_valid_metrics"] is True
    assert res["sharpe"] == 1.45
    assert res["fitness"] == 1.12
    assert res["turnover"] == 0.35
    assert res["margin_bps"] == 6.2


def test_parse_empty_portfolio_response():
    data = {
        "records": [],
        "stats": {
            "longCount": 0,
            "shortCount": 0
        }
    }

    res = response_parser.parse_simulation_response(data)
    assert res["classification"] == "TECHNICAL_FAILURE"
    assert res["portfolio_status"] == "EMPTY"
    assert res["metrics_status"] == "MISSING"
    assert res["has_valid_metrics"] is False
    # CRITICAL: Missing Sharpe is None, NEVER 0.0
    assert res["sharpe"] is None
    assert res["fitness"] is None


def test_parse_error_response():
    data = {
        "error": "Syntax error in expression: unknown token",
        "message": "Compilation failed"
    }

    res = response_parser.parse_simulation_response(data)
    assert res["classification"] == "TECHNICAL_FAILURE"
    assert res["has_valid_metrics"] is False
    assert res["sharpe"] is None
    assert res["fitness"] is None
    assert "error" in res["diagnostic_reason"].lower()
