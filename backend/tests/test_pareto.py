import pytest
from backend.app.research.pareto import pareto_engine


def test_pareto_dominance():
    # A dominates B if Sharpe >=, Fitness >=, Turnover <=, and at least one strictly better
    cand_a = {"id": "a", "sharpe": 1.6, "fitness": 1.2, "turnover": 0.3, "margin_bps": 5.0}
    cand_b = {"id": "b", "sharpe": 1.4, "fitness": 1.0, "turnover": 0.5, "margin_bps": 4.0}
    cand_c = {"id": "c", "sharpe": 1.8, "fitness": 1.5, "turnover": 0.6, "margin_bps": 6.0}

    assert pareto_engine.dominates(cand_a, cand_b) is True
    assert pareto_engine.dominates(cand_b, cand_a) is False

    # Cand C has higher Sharpe but higher Turnover -> neither strictly dominates across all axes
    assert pareto_engine.dominates(cand_a, cand_c) is False
    assert pareto_engine.dominates(cand_c, cand_a) is False


def test_compute_pareto_front():
    candidates = [
        {"id": "a", "sharpe": 1.6, "fitness": 1.2, "turnover": 0.3, "margin_bps": 5.0},
        {"id": "b", "sharpe": 1.4, "fitness": 1.0, "turnover": 0.5, "margin_bps": 4.0},
        {"id": "c", "sharpe": 1.8, "fitness": 1.5, "turnover": 0.2, "margin_bps": 7.0},
    ]

    results = pareto_engine.compute_pareto_front(candidates)
    
    # Candidate c dominates both a and b (higher Sharpe, higher fitness, lower turnover)
    c_res = next(r for r in results if r["id"] == "c")
    assert c_res["is_pareto_optimal"] is True
    assert c_res["pareto_rank"] == 1
