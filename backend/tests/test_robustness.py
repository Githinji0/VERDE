import pytest
from backend.app.research.robustness import robustness_engine
from backend.app.research.walk_forward import walk_forward_engine


def test_robustness_evaluation_stable():
    base_sharpe = 1.50
    perturbed = [1.45, 1.48, 1.40, 1.52, 1.42]

    res = robustness_engine.evaluate_robustness(base_sharpe, perturbed)
    assert res["overall_robustness_score"] >= 0.85
    assert res["stability_grade"] == "ROBUST"


def test_robustness_evaluation_fragile():
    base_sharpe = 1.60
    # Severe degradation under parameter perturbation
    perturbed = [0.30, 0.40, 0.20, 0.10]

    res = robustness_engine.evaluate_robustness(base_sharpe, perturbed)
    assert res["overall_robustness_score"] < 0.40
    assert res["stability_grade"] == "FRAGILE"


def test_walk_forward_degradation():
    # Healthy alpha retention
    healthy = walk_forward_engine.calculate_degradation(is_sharpe=1.60, oos_sharpe=1.35)
    assert healthy["degradation_ratio"] >= 0.80
    assert healthy["verdict"] == "STABLE"

    # Severe overfit
    overfit = walk_forward_engine.calculate_degradation(is_sharpe=1.80, oos_sharpe=0.40)
    assert overfit["degradation_ratio"] < 0.30
    assert overfit["verdict"] == "OVERFIT_WARNING"
