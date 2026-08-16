from typing import Any, Dict, Optional


class WalkForwardEngine:
    """Evaluates In-Sample (IS) vs. Out-of-Sample (OOS) performance degradation."""

    @staticmethod
    def calculate_degradation(
        is_sharpe: Optional[float],
        oos_sharpe: Optional[float]
    ) -> Dict[str, Any]:
        """
        Measures ratio of OOS Sharpe to IS Sharpe.
        Healthy alphas retain >= 70% of IS Sharpe out-of-sample.
        """
        if is_sharpe is None or oos_sharpe is None:
            return {
                "in_sample_sharpe": is_sharpe,
                "out_of_sample_sharpe": oos_sharpe,
                "degradation_ratio": None,
                "stability_score": None,
                "verdict": "INSUFFICIENT_DATA"
            }

        if is_sharpe <= 0:
            ratio = 0.0
        else:
            ratio = round(oos_sharpe / is_sharpe, 3)

        stability = max(0.0, min(1.0, ratio))
        
        verdict = "STABLE" if ratio >= 0.70 else ("OVERFIT_WARNING" if ratio < 0.40 else "MODERATE_DECAY")

        return {
            "in_sample_sharpe": is_sharpe,
            "out_of_sample_sharpe": oos_sharpe,
            "degradation_ratio": ratio,
            "stability_score": stability,
            "verdict": verdict
        }


walk_forward_engine = WalkForwardEngine()
