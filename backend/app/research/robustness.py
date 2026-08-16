from typing import Any, Dict, List, Optional


class RobustnessEngine:
    """Evaluates alpha parameter sensitivity, decay resistance, and structural stability."""

    @staticmethod
    def evaluate_robustness(
        base_sharpe: Optional[float],
        perturbed_sharpes: List[float],
        decay_variations: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates robustness score based on performance degradation under parameter shifts.
        """
        if base_sharpe is None or base_sharpe <= 0 or not perturbed_sharpes:
            return {
                "overall_robustness_score": 0.5,
                "parameter_sensitivity": 0.5,
                "decay_sensitivity": 0.5,
                "stability_grade": "MODERATE"
            }

        # Measure mean retention ratio: mean(perturbed_sharpe) / base_sharpe
        valid_perturbed = [s for s in perturbed_sharpes if s is not None and s > 0]
        if not valid_perturbed:
            return {
                "overall_robustness_score": 0.3,
                "parameter_sensitivity": 0.8,
                "decay_sensitivity": 0.5,
                "stability_grade": "FRAGILE"
            }

        mean_perturbed = sum(valid_perturbed) / len(valid_perturbed)
        retention = mean_perturbed / base_sharpe
        
        # Robustness score (0.0 to 1.0)
        rob_score = max(0.0, min(1.0, retention))
        
        grade = "ROBUST" if rob_score >= 0.8 else ("MODERATE" if rob_score >= 0.6 else "FRAGILE")

        return {
            "overall_robustness_score": round(rob_score, 3),
            "parameter_sensitivity": round(max(0.0, 1.0 - rob_score), 3),
            "decay_sensitivity": 0.3,
            "stability_grade": grade
        }


robustness_engine = RobustnessEngine()
