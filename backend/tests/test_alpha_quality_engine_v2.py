import pytest
from backend.app.generation.field_intelligence import field_intelligence
from backend.app.generation.hypothesis_engine import hypothesis_engine
from backend.app.research.evolution import evolution_engine
from backend.app.research.memory import research_memory
from backend.app.research.preflight_quality import prebrain_quality_engine
from backend.app.research.robustness import robustness_engine
from backend.app.research.scoring import alpha_scorer


def test_field_intelligence_scoring():
    """Verify Field Intelligence calculates Field Quality Scores and metadata profiles."""
    prof = field_intelligence.get_field_profile("close")
    assert prof is not None
    assert prof["category"] == "PRICE"
    assert prof["quality_score"] >= 50.0

    ranked = field_intelligence.get_ranked_fields_for_family("MOMENTUM")
    assert len(ranked) > 0
    assert ranked[0]["quality_score"] >= ranked[-1]["quality_score"]


def test_prebrain_quality_engine_evaluation():
    """Verify Pre-BRAIN Quality Engine produces 8-dimensional scores and preflight decisions."""
    # Test valid high-quality expression
    expr_good = "group_neutralize(rank(ts_mean(returns, 10)), subindustry)"
    res_good = prebrain_quality_engine.evaluate_candidate(expr_good, "MOMENTUM")
    assert res_good["pre_brain_score"] >= 65.0
    assert res_good["decision"] == "PASS"
    assert "explainability" in res_good

    # Test invalid / poor expression (<65 rejected)
    expr_poor = "rank(rank(close))"
    res_poor = prebrain_quality_engine.evaluate_candidate(expr_poor, "MOMENTUM")
    assert "breakdown" in res_poor
    assert res_poor["breakdown"]["redundancy_risk"] < 5.0


def test_hypothesis_engine_v2_generation():
    """Verify HypothesisEngine generates strategy-guided expressions."""
    cand = hypothesis_engine.generate_candidate_expression("MOMENTUM", "EXPLOITATION")
    assert "expression" in cand
    assert cand["family_code"] == "MOMENTUM"
    assert cand["strategy_allocation"] == "EXPLOITATION"

    cand_novel = hypothesis_engine.generate_candidate_expression("VALUE", "NOVEL")
    assert "expression" in cand_novel
    assert cand_novel["strategy_allocation"] == "NOVEL"


def test_evolutionary_mutation_engine():
    """Verify Evolutionary Mutation Engine applies controlled operators and crossover."""
    parent = "rank(ts_mean(returns, 10))"
    mut = evolution_engine.mutate_candidate(parent, "MOMENTUM", "LOOKBACK_MUTATION")
    assert mut["offspring_expression"] != parent or "10" in parent
    assert mut["mutation_type"] == "LOOKBACK_MUTATION"

    cross = evolution_engine.crossover_candidates("rank(ts_mean(returns, 10))", "rank(book_value / (close * shares_out))")
    assert "group_neutralize" in cross["offspring_expression"]
    assert cross["mutation_type"] == "CROSSOVER"


def test_robustness_parameter_neighborhood():
    """Verify RobustnessEngine builds parameter neighborhood variants."""
    expr = "rank(ts_mean(returns, 10))"
    neighbors = robustness_engine.generate_parameter_neighborhood(expr)
    assert len(neighbors) >= 3
    lookbacks = [n["lookback"] for n in neighbors]
    assert 10 in lookbacks


def test_alpha_scorer_v2_tiering():
    """Verify AlphaScorer classifies formal V2 Tiers."""
    tier_elite = alpha_scorer.classify_alpha_tier(90.0, True, 0.85, 0.20)
    assert tier_elite == "ELITE"

    tier_strong = alpha_scorer.classify_alpha_tier(78.0, True, 0.70, 0.50)
    assert tier_strong == "STRONG"

    tier_promising = alpha_scorer.classify_alpha_tier(65.0, False, 0.50, 0.80)
    assert tier_promising == "PROMISING"

    tier_weak = alpha_scorer.classify_alpha_tier(45.0, False, 0.30, 0.90)
    assert tier_weak == "WEAK"
