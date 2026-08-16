import re
from typing import Any, Dict, List, Optional
from backend.app.config import settings


def classify_candidate_tier(
    classification: str,
    preflight_decision: str,
    sharpe: Optional[float],
    fitness: Optional[float],
    turnover: Optional[float],
    is_pareto: bool = False
) -> str:
    """Classifies an alpha candidate into defined research quality tiers (Tier 0 to Tier 6)."""
    if classification == "TECHNICAL_FAILURE":
        return "TIER_0_TECHNICAL_FAILURE"
    if classification == "PORTFOLIO_EMPTY":
        return "TIER_1_PORTFOLIO_EMPTY"
    if classification in ("ALPHA_FAILURE", "AUTH_FAILURE", "REMOTE_FAILURE"):
        return "TIER_1_SIMULATION_FAILED"
    if preflight_decision == "REJECT":
        return "TIER_1_PREFLIGHT_REJECTED"
    if sharpe is None or fitness is None:
        return "TIER_1_PREFLIGHT_PENDING"

    # Passing configured targets
    if sharpe >= settings.MIN_SHARPE and fitness >= settings.MIN_FITNESS and (turnover is None or turnover <= settings.MAX_TURNOVER):
        if is_pareto:
            return "TIER_6_CANDIDATE_READY_PARETO"
        return "TIER_5_HIGH_QUALITY"

    # Near Miss
    if (settings.NEAR_MISS_MIN_SHARPE <= sharpe <= settings.NEAR_MISS_MAX_SHARPE) or (settings.NEAR_MISS_MIN_FITNESS <= fitness <= settings.NEAR_MISS_MAX_FITNESS):
        return "TIER_3_NEAR_MISS"

    if sharpe >= 0.8:
        return "TIER_4_PROMISING"

    return "TIER_2_VALID_WEAK"


class CandidateOptimizer:
    """Mutates near-miss and high-turnover alpha expressions to improve Sharpe and Turnover."""

    @staticmethod
    def mutate_lookback(expression: str, delta: int = 5) -> str:
        """Perturbs the first found rolling integer lookback."""
        def repl(match):
            val = int(match.group(1))
            new_val = max(2, val + delta)
            return f", {new_val})"

        return re.sub(r',\s*(\d+)\)', repl, expression, count=1)

    @staticmethod
    def apply_turnover_reduction(expression: str) -> str:
        """Applies signal smoothing or volatility normalization to tame high turnover."""
        if "ts_mean(" not in expression:
            return f"ts_mean({expression}, 3)"
        return f"rank({expression} / (ts_std_dev(returns, 20) + 0.0001))"

    @staticmethod
    def apply_group_neutralization(expression: str, group: str = "subindustry") -> str:
        """Enforces industry neutralization on raw signal."""
        if "group_neutralize(" in expression:
            # Swap group to industry or sector
            if "subindustry" in expression:
                return expression.replace("subindustry", "industry")
            elif "industry" in expression:
                return expression.replace("industry", "sector")
            return expression
        return f"group_neutralize({expression}, {group})"

    @classmethod
    def generate_mutations(cls, expression: str, candidate_id: str) -> List[Dict[str, Any]]:
        """Generates a suite of targeted mutations for a near-miss candidate."""
        mutations = []

        # 1. Lookback perturbations
        mutations.append({
            "expression": cls.mutate_lookback(expression, delta=+5),
            "mutation_type": "LOOKBACK_INCREASE",
            "changed_lookback": 5,
            "generation_reason": "Extended lookback horizon for noise reduction."
        })
        mutations.append({
            "expression": cls.mutate_lookback(expression, delta=-5),
            "mutation_type": "LOOKBACK_DECREASE",
            "changed_lookback": -5,
            "generation_reason": "Shortened lookback horizon for faster trend capture."
        })

        # 2. Turnover smoothing
        mutations.append({
            "expression": cls.apply_turnover_reduction(expression),
            "mutation_type": "TURNOVER_SMOOTHING",
            "changed_transformation": "ts_mean / vol_norm",
            "generation_reason": "Applied rolling signal filter to control turnover."
        })

        # 3. Neutralization adjustment
        mutations.append({
            "expression": cls.apply_group_neutralization(expression, "subindustry"),
            "mutation_type": "GROUP_NEUTRALIZATION",
            "changed_group": "subindustry",
            "generation_reason": "Neutralized signal across subindustry peer groups."
        })

        return mutations


candidate_optimizer = CandidateOptimizer()
