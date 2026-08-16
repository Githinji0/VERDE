import pytest
from backend.app.research.diagnostics import SimulationDiagnosticEngine, simulation_diagnostics


def test_diagnose_valid_metrics():
    raw = {
        "stats": {
            "longCount": 120,
            "shortCount": 115,
            "sharpe": 1.65,
            "fitness": 1.35,
            "turnover": 0.28,
            "margin": 7.2
        },
        "records": [{"pnl": 500}]
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="rank(ts_mean(returns, 10))",
        http_status=200,
        simulation_id="SIM-VALID-01",
        brain_sim_id="BRAIN-100"
    )

    assert diag["classification"] == "VALID_METRICS"
    assert diag["portfolio_state"] == "VALID"
    assert diag["metrics_state"] == "AVAILABLE"
    assert diag["has_valid_metrics"] is True
    assert diag["sharpe"] == 1.65
    assert diag["position_count"] == 235


def test_diagnose_empty_portfolio():
    raw = {
        "stats": {
            "longCount": 0,
            "shortCount": 0,
            "turnover": 0.0
        },
        "records": []
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="rank(close)",
        http_status=200,
        simulation_id="SIM-EMPTY-01",
        brain_sim_id="BRAIN-101"
    )

    assert diag["classification"] == "PORTFOLIO_EMPTY"
    assert diag["portfolio_state"] == "EMPTY"
    assert diag["metrics_state"] == "UNAVAILABLE"
    assert diag["has_valid_metrics"] is False
    assert diag["sharpe"] is None
    assert diag["fitness"] is None


def test_diagnose_auth_failure():
    raw = {"message": "Unauthorized session token"}

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="close",
        http_status=401,
        simulation_id="SIM-AUTH-01"
    )

    assert diag["classification"] == "AUTH_FAILURE"
    assert diag["diagnostic_code"] == "AUTH_FAILED"
    assert diag["root_cause"]["type"] == "AUTHENTICATION_FAILURE"


def test_diagnose_rate_limit_failure():
    raw = {"message": "Rate limit exceeded"}

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="close",
        http_status=429,
        simulation_id="SIM-RATE-01"
    )

    assert diag["classification"] == "REMOTE_FAILURE"
    assert diag["diagnostic_code"] == "RATE_LIMITED"


def test_diagnose_alpha_compilation_failure():
    raw = {
        "error": "Syntax error: invalid token 'invalid_field'",
        "message": "Compilation failed"
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="invalid_field + 1",
        http_status=200,
        simulation_id="SIM-ALPHA-FAIL"
    )

    assert diag["classification"] == "ALPHA_FAILURE"
    assert diag["diagnostic_code"] == "COMPILATION_ERROR"
    assert diag["root_cause"]["type"] == "SYNTAX_OR_FIELD_ERROR"


def test_diagnose_parser_failure_on_non_dict():
    from backend.app.brain.response_parser import response_parser

    res = response_parser.parse_simulation_response("not a dictionary string")
    assert res["classification"] == "PARSER_FAILURE"
    assert res["diagnostic_code"] == "INVALID_RESPONSE_TYPE"


def test_diagnose_affected_alpha_potential_redundant_neutralization():
    raw = {
        "stats": {
            "longCount": 0,
            "shortCount": 0,
            "turnover": 0.0
        },
        "records": []
    }

    expr = "group_neutralize(rank(ts_mean(returns, 10)), subindustry)"
    settings = {
        "universe": "TOP3000",
        "region": "USA",
        "delay": 1,
        "neutralization": "SUBINDUSTRY",
        "truncation": 0.08
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression=expr,
        settings_dict=settings,
        http_status=200,
        simulation_id="SIM-dca88a4c",
        brain_sim_id="3GMHGdbv50zuhGXfWd5kq"
    )

    assert diag["classification"] == "PORTFOLIO_EMPTY"
    assert diag["remote_status"] == "PORTFOLIO_EMPTY"
    assert diag["portfolio_state"] == "EMPTY"
    assert diag["metrics_state"] == "UNAVAILABLE"
    assert diag["root_cause"]["type"] == "POTENTIAL_REDUNDANT_NEUTRALIZATION"
    assert diag["root_cause"]["confidence"] == "LOW"
    assert diag["why_not_proven"] is not None
    assert "complete portfolio collapse at this stage cannot be confirmed" in diag["why_not_proven"]
    
    ev_cat = diag["evidence_categorized"]
    assert len(ev_cat["observed"]) >= 2
    assert len(ev_cat["unknown"]) >= 2
    assert len(diag["recommended_experiments"]) >= 2
    assert diag["position_pipeline"]["last_nonzero_stage"].startswith("universe_count")


def test_diagnose_measured_neutralization_collapse_high_confidence():
    raw = {
        "post_neutralization_weights": 0,
        "stats": {
            "longCount": 0,
            "shortCount": 0
        }
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="group_neutralize(rank(close), subindustry)",
        http_status=200,
        simulation_id="SIM-MEASURED-01"
    )

    assert diag["classification"] == "PORTFOLIO_EMPTY"
    assert diag["root_cause"]["type"] == "NEUTRALIZATION_COLLAPSE"
    assert diag["root_cause"]["confidence"] == "HIGH"
    assert diag["why_not_proven"] is None


def test_diagnose_unobservable_signal_stats():
    raw = {
        "stats": {
            "longCount": 0,
            "shortCount": 0
        }
    }

    diag = simulation_diagnostics.diagnose_simulation(
        raw_response=raw,
        expression="rank(ts_mean(returns, 20))",
        http_status=200
    )

    assert diag["signal_stats"]["status"] == "NOT_OBSERVABLE"
    assert diag["signal_stats"]["is_constant"] == "UNKNOWN"
    assert diag["signal_stats"]["min"] is None


def test_secret_redaction_in_telemetry():
    raw = {
        "session_cookie": "secret_cookie_12345",
        "auth_token": "Bearer abc.def.ghi",
        "stats": {
            "longCount": 50,
            "shortCount": 50
        }
    }

    sanitized = SimulationDiagnosticEngine.sanitize_telemetry(raw)
    assert sanitized["session_cookie"] == "[REDACTED]"
    assert sanitized["auth_token"] == "[REDACTED]"
    assert sanitized["stats"]["longCount"] == 50
