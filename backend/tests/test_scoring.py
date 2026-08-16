import pytest
from backend.app.research.optimization import classify_candidate_tier
from backend.app.research.scoring import alpha_scorer


def test_research_score_calculation_valid():
    score_data = alpha_scorer.calculate_research_score(
        sharpe=1.55,
        fitness=1.20,
        turnover=0.30,
        margin_bps=6.5,
        complexity=2.0
    )
    assert score_data is not None
    assert score_data["total_score"] > 50.0
    assert score_data["is_target_passing"] is True
    assert score_data["is_candidate_ready"] is True


def test_research_score_none_on_missing_metrics():
    # Missing Sharpe should return None, not a bogus 0 score
    assert alpha_scorer.calculate_research_score(None, 1.20, 0.30, 6.0) is None
    assert alpha_scorer.calculate_research_score(1.50, None, 0.30, 6.0) is None


def test_candidate_tiering():
    # Technical failure -> Tier 0
    assert classify_candidate_tier("TECHNICAL_FAILURE", "PASS", None, None, None) == "TIER_0_TECHNICAL_FAILURE"
    
    # Preflight rejected -> Tier 1
    assert classify_candidate_tier("PENDING", "REJECT", None, None, None) == "TIER_1_PREFLIGHT_REJECTED"
    
    # Near miss (Sharpe 1.15, Fitness 0.90) -> Tier 3
    assert classify_candidate_tier("VALID_METRICS", "PASS", 1.15, 0.90, 0.40) == "TIER_3_NEAR_MISS"
    
    # Passing targets with Pareto -> Tier 6
    assert classify_candidate_tier("VALID_METRICS", "PASS", 1.60, 1.25, 0.35, is_pareto=True) == "TIER_6_CANDIDATE_READY_PARETO"
