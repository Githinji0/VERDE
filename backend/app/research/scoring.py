from typing import Any, Dict, Optional
from backend.app.config import settings


class AlphaScorer:
    """Calculates weighted research scores and complexity penalties for simulated alpha candidates."""

    @staticmethod
    def calculate_research_score(
        sharpe: Optional[float],
        fitness: Optional[float],
        turnover: Optional[float],
        margin_bps: Optional[float],
        complexity: float = 1.0,
        robustness: Optional[float] = None,
        stability: Optional[float] = None,
        diversity: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculates normalized research score.
        Returns None if essential metrics (Sharpe/Fitness) are missing (no false zeroes).
        """
        if sharpe is None or fitness is None:
            return None

        # Normalized components (0.0 to 1.0)
        # Sharpe component: target ~ 1.5+
        s_norm = max(0.0, min(1.0, (sharpe - 0.5) / 1.5)) if sharpe > 0 else 0.0
        
        # Fitness component: target ~ 1.2+
        f_norm = max(0.0, min(1.0, fitness / 1.5)) if fitness > 0 else 0.0
        
        # Turnover component: lower is better (optimal < 0.30)
        if turnover is not None:
            t_norm = max(0.0, min(1.0, 1.0 - (turnover / 1.0)))
        else:
            t_norm = 0.5

        # Robustness & Stability
        rob_norm = robustness if robustness is not None else 0.7
        stab_norm = stability if stability is not None else 0.7
        div_norm = diversity if diversity is not None else 0.8
        
        # Simplicity (penalizes high complexity > 5.0)
        simp_norm = max(0.0, min(1.0, 1.0 - ((complexity - 1.0) / 10.0)))
        comp_penalty = round(max(0.0, (complexity - 3.0) * 0.02), 4)

        # Weighted calculation
        raw_score = (
            settings.WEIGHT_SHARPE * s_norm +
            settings.WEIGHT_FITNESS * f_norm +
            settings.WEIGHT_TURNOVER * t_norm +
            settings.WEIGHT_STABILITY * stab_norm +
            settings.WEIGHT_ROBUSTNESS * rob_norm +
            settings.WEIGHT_DIVERSITY * div_norm +
            settings.WEIGHT_SIMPLICITY * simp_norm
        )
        total_score = round(max(0.0, raw_score - comp_penalty) * 100, 2)

        is_target_passing = bool(
            sharpe >= settings.MIN_SHARPE and
            fitness >= settings.MIN_FITNESS and
            (turnover is None or turnover <= settings.MAX_TURNOVER) and
            (margin_bps is None or margin_bps >= settings.MIN_MARGIN_BPS)
        )

        is_candidate_ready = bool(
            is_target_passing and
            rob_norm >= 0.6 and
            complexity <= 7.0
        )

        return {
            "total_score": total_score,
            "sharpe_component": round(s_norm, 3),
            "fitness_component": round(f_norm, 3),
            "turnover_component": round(t_norm, 3),
            "stability_component": round(stab_norm, 3),
            "robustness_component": round(rob_norm, 3),
            "diversity_component": round(div_norm, 3),
            "simplicity_component": round(simp_norm, 3),
            "complexity_penalty": comp_penalty,
            "is_target_passing": is_target_passing,
            "is_candidate_ready": is_candidate_ready,
            "tier": AlphaScorer.classify_alpha_tier(total_score, is_candidate_ready, rob_norm)
        }

    @staticmethod
    def classify_alpha_tier(
        total_score: Optional[float],
        is_candidate_ready: bool,
        robustness: float = 0.7,
        correlation: float = 0.0
    ) -> str:
        """Classifies formal V2 Alpha Tiers: ELITE, STRONG, PROMISING, WEAK."""
        if total_score is None:
            return "UNKNOWN"
        if total_score >= 85.0 and is_candidate_ready and robustness >= 0.75 and correlation <= 0.70:
            return "ELITE"
        if total_score >= 75.0 and is_candidate_ready:
            return "STRONG"
        if total_score >= 60.0:
            return "PROMISING"
        return "WEAK"


alpha_scorer = AlphaScorer()

