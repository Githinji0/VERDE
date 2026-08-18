from typing import Any, Dict, List, Optional
from backend.app.generation.ast_parser import ast_parser
from backend.app.generation.field_intelligence import field_intelligence
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash


class PreBrainQualityEngine:
    """
    Pre-BRAIN Quality Engine V2.
    Evaluates candidate expressions before BRAIN submission across 8 dimensions.
    Produces PRE_BRAIN_SCORE (0-100) and decides priority allocation / preflight rejection (<65).
    """

    def __init__(self):
        self.rejection_threshold = 65.0

    def evaluate_candidate(
        self,
        expression: str,
        family_code: str,
        hypothesis: Optional[str] = None,
        simulation_neutralization: str = "SUBINDUSTRY",
        existing_hashes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate expression quality before BRAIN submission.
        """
        # 1. Parse AST
        components = ast_parser.extract_component_hierarchy(expression)
        root_info = components[-1] if components else {}
        expr_hash = compute_expression_hash(expression)
        struct_hash = compute_structure_hash(expression)

        # Extract fields and operators used
        fields_used = [c["expression"] for c in components if c["stage"] == "BASE_FIELD"]
        operators_used = [c["expression"].split("(")[0] for c in components if "(" in c["expression"]]

        # --- Sub-Score 1: Semantic Quality (20 max) ---
        semantic_score = 20.0
        if not expression or len(expression.strip()) < 3:
            semantic_score = 0.0

        # --- Sub-Score 2: Field Quality (15 max) ---
        field_scores = []
        for f in fields_used:
            prof = field_intelligence.get_field_profile(f)
            if prof:
                field_scores.append(prof["quality_score"])
            else:
                field_scores.append(70.0)
        avg_field_qual = sum(field_scores) / len(field_scores) if field_scores else 80.0
        field_score_weighted = min(15.0, (avg_field_qual / 100.0) * 15.0)

        # --- Sub-Score 3: Signal Variation (15 max) ---
        # Checks if signal has rank or group_neutralize to guarantee cross-sectional variation
        has_rank = any("rank" in op for op in operators_used)
        has_neut = any("neutralize" in op for op in operators_used)
        signal_var_score = 15.0 if (has_rank or has_neut) else 10.0

        # --- Sub-Score 4: Temporal Quality (15 max) ---
        temporal_score = 15.0
        # Check for excessive smoothing or invalid lookbacks
        if "ts_mean" in expression and "ts_mean(ts_mean" in expression:
            temporal_score -= 5.0
        if "ts_delay" in expression and "0" in expression:
            temporal_score -= 3.0

        # --- Sub-Score 5: Hypothesis Strength (10 max) ---
        hypothesis_score = 10.0
        if family_code == "MOMENTUM" and not any(op in expression for op in ["ts_delta", "ts_mean", "rank", "ts_delay"]):
            hypothesis_score = 5.0

        # --- Sub-Score 6: Complexity Cost (10 max) ---
        depth = len(components)
        complexity_score = 10.0
        if depth > 6:
            complexity_score = 5.0
        elif depth > 8:
            complexity_score = 2.0

        # --- Sub-Score 7: Novelty Score (10 max) ---
        novelty_score = 10.0
        if existing_hashes and expr_hash in existing_hashes:
            novelty_score = 0.0

        # --- Sub-Score 8: Redundancy Risk (5 max) ---
        redundancy_penalty = 0.0
        redundancy_notes = []
        if f"group_neutralize(" in expression and simulation_neutralization.lower() in expression.lower():
            redundancy_penalty += 2.0
            redundancy_notes.append("Potential formula and simulation neutralization overlap.")
        if "rank(rank(" in expression.replace(" ", ""):
            redundancy_penalty += 3.0
            redundancy_notes.append("Redundant nested rank operator.")

        redundancy_score = max(0.0, 5.0 - redundancy_penalty)

        # Calculate Total Pre-BRAIN Score (0 - 100)
        total_score = round(
            semantic_score + field_score_weighted + signal_var_score +
            temporal_score + hypothesis_score + complexity_score +
            novelty_score + redundancy_score, 1
        )
        total_score = max(0.0, min(100.0, total_score))

        # Priority Decision Allocation
        if total_score < self.rejection_threshold:
            decision = "REJECT"
            bucket = "REJECTED"
        elif total_score >= 90.0:
            decision = "PASS"
            bucket = "PREMIUM_CANDIDATE"
        elif total_score >= 85.0:
            decision = "PASS"
            bucket = "HIGH_PRIORITY"
        elif total_score >= 75.0:
            decision = "PASS"
            bucket = "SUBMIT"
        else:
            decision = "PASS"
            bucket = "LOW_PRIORITY"

        reason = f"Pre-BRAIN Score: {total_score}/100. Category: {bucket}."
        if redundancy_notes:
            reason += " " + " ".join(redundancy_notes)

        return {
            "pre_brain_score": total_score,
            "decision": decision,
            "priority_bucket": bucket,
            "reason": reason,
            "expression_hash": expr_hash,
            "structure_hash": struct_hash,
            "fields_used": fields_used,
            "operators_used": operators_used,
            "complexity_score": depth,
            "breakdown": {
                "semantic": semantic_score,
                "field_quality": field_score_weighted,
                "signal_variation": signal_var_score,
                "temporal_quality": temporal_score,
                "hypothesis_strength": hypothesis_score,
                "complexity": complexity_score,
                "novelty": novelty_score,
                "redundancy_risk": redundancy_score
            },
            "explainability": {
                "hypothesis": hypothesis or f"Hypothesis for {family_code} family",
                "field_selection_rationale": f"Selected high-quality fields ({', '.join(fields_used) if fields_used else 'N/A'}) based on category compatibility.",
                "operator_rationale": f"Applied operators ({', '.join(set(operators_used)) if operators_used else 'N/A'}) to model expected temporal dynamics.",
                "pre_brain_evaluation": f"Scored {total_score}/100 across 8 quality dimensions."
            }
        }


prebrain_quality_engine = PreBrainQualityEngine()
