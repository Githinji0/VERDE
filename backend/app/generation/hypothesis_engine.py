import random
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import AlphaCandidate, PreflightResult, ResearchExperiment
from backend.app.generation.family_info import RESEARCH_FAMILIES
from backend.app.generation.field_intelligence import field_intelligence
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash
from backend.app.research.preflight_quality import prebrain_quality_engine


class HypothesisEngine:
    """
    Hypothesis Engine V2 for VERDE Alpha Quality Engine V2.
    Generates research-hypothesis driven alpha candidates using:
    - 40% Exploitation (High-quality field intelligence & proven templates)
    - 20% Evolution / Mutations (Evolving successful parent candidates)
    - 15% Research Gap Exploration (Targeting underexplored field/operator combinations)
    - 10% Cross-Family Composite Synthesis
    - 10% Simplification & Refinement
    - 5% Novel Experimental
    Integrates Pre-BRAIN Quality Engine (<65 rejected before BRAIN submission).
    """

    def __init__(self):
        self.families = RESEARCH_FAMILIES

    def generate_candidate_expression(
        self,
        family_code: str = "MOMENTUM",
        strategy_allocation: str = "EXPLOITATION"
    ) -> Dict[str, Any]:
        """
        Synthesizes candidate expression guided by strategy allocation and Field Intelligence.
        """
        family = self.families.get(family_code, self.families["MOMENTUM"])
        hypothesis = family["core_hypothesis"]
        
        # Rank fields for this family using Field Intelligence
        ranked_fields = field_intelligence.get_ranked_fields_for_family(family_code)
        primary_field = ranked_fields[0]["field"] if ranked_fields else "close"
        secondary_field = ranked_fields[1]["field"] if len(ranked_fields) > 1 else "returns"

        templates = family.get("templates", ["rank(close / ts_delay(close, 20) - 1)"])
        template = random.choice(templates)

        lookbacks = [5, 10, 15, 20, 30, 40, 60] if family["temporal_behavior"] == "FAST" else [60, 120, 252]
        lookback = random.choice(lookbacks)

        expr = template.replace("{lookback}", str(lookback))
        if primary_field != "close" and "close" in expr:
            expr = expr.replace("close", primary_field)

        # Apply strategy-specific transformations
        if strategy_allocation == "GAP_EXPLORATION":
            expr = f"group_neutralize(rank({primary_field} / (ts_std_dev({secondary_field}, {lookback}) + 0.0001)), subindustry)"
        elif strategy_allocation == "COMPOSITE":
            expr = f"group_neutralize(0.5 * {expr} + 0.5 * rank({secondary_field}), subindustry)"
        elif strategy_allocation == "SIMPLIFICATION":
            expr = f"rank(ts_mean({primary_field}, {lookback}))"
        elif strategy_allocation == "NOVEL":
            expr = f"group_neutralize(rank(ts_zscore({primary_field}, {lookback}) * rank({secondary_field})), industry)"

        return {
            "expression": expr,
            "family_code": family_code,
            "hypothesis": hypothesis,
            "strategy_allocation": strategy_allocation,
            "lookback": lookback,
            "primary_field": primary_field,
            "secondary_field": secondary_field
        }

    async def generate_and_preflight_candidates(
        self,
        family_code: str = "MOMENTUM",
        count: int = 10,
        proven_ratio: Optional[float] = None,
        explored_ratio: Optional[float] = None,
        novel_ratio: Optional[float] = None,
        experiment_id: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        existing_hashes: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generates a batch of candidates, runs Pre-BRAIN Quality evaluation, and persists records.
        Filter candidates below Pre-BRAIN Quality threshold (<65) before BRAIN submission.
        """
        results = []
        
        for _ in range(count):
            # Sample strategy allocation according to V2 ratios
            r = random.random()
            if r < 0.40:
                strat = "EXPLOITATION"
            elif r < 0.60:
                strat = "MUTATION"
            elif r < 0.75:
                strat = "GAP_EXPLORATION"
            elif r < 0.85:
                strat = "COMPOSITE"
            elif r < 0.95:
                strat = "SIMPLIFICATION"
            else:
                strat = "NOVEL"

            cand_info = self.generate_candidate_expression(family_code, strat)
            expr = cand_info["expression"]

            # Run Pre-BRAIN Quality Engine Evaluation
            eval_res = prebrain_quality_engine.evaluate_candidate(
                expression=expr,
                family_code=family_code,
                hypothesis=cand_info["hypothesis"],
                existing_hashes=existing_hashes
            )

            cand_id = None
            if session:
                expr_hash = eval_res["expression_hash"]
                struct_hash = eval_res["structure_hash"]

                preflight_status = "PASS" if eval_res["decision"] == "PASS" else "REJECT"
                tier = f"TIER_{eval_res['priority_bucket']}"

                candidate = AlphaCandidate(
                    expression=expr,
                    expression_hash=expr_hash,
                    structure_hash=struct_hash,
                    family_code=family_code,
                    fields_used=eval_res["fields_used"],
                    operators_used=eval_res["operators_used"],
                    complexity_score=eval_res["complexity_score"],
                    preflight_status=preflight_status,
                    preflight_reason=eval_res["reason"],
                    compatibility_score=eval_res["breakdown"]["semantic"] / 20.0,
                    constant_signal_risk=1.0 - (eval_res["breakdown"]["signal_variation"] / 15.0),
                    pre_brain_score=eval_res["pre_brain_score"],
                    novelty_score=eval_res["breakdown"]["novelty"] * 10.0,
                    tier=tier,
                    lifecycle_state="PREFLIGHT" if preflight_status == "PASS" else "PREFLIGHT_REJECTED",
                    priority_bucket=strat,
                    experiment_id=experiment_id,
                    generation_reason=f"Generated via {strat} strategy for {family_code} family.",
                    explainability_rationale=eval_res["explainability"]
                )
                session.add(candidate)
                await session.flush()
                cand_id = candidate.id

                preflight_rec = PreflightResult(
                    candidate_id=candidate.id,
                    decision=preflight_status,
                    reason=eval_res["reason"],
                    compatibility_score=eval_res["breakdown"]["semantic"] / 20.0,
                    constant_signal_risk=1.0 - (eval_res["breakdown"]["signal_variation"] / 15.0),
                    complexity_score=eval_res["complexity_score"],
                    diagnostic_details=eval_res["breakdown"]
                )
                session.add(preflight_rec)

                # Update experiment stats if linked
                if experiment_id:
                    exp = await session.get(ResearchExperiment, experiment_id)
                    if exp:
                        exp.candidates_generated += 1
                        if preflight_status == "REJECT":
                            exp.candidates_rejected_preflight += 1

                await session.commit()

            results.append({
                "id": cand_id,
                "expression": expr,
                "family_code": family_code,
                "hypothesis": cand_info["hypothesis"],
                "strategy_allocation": strat,
                "pre_brain_score": eval_res["pre_brain_score"],
                "decision": eval_res["decision"],
                "priority_bucket": eval_res["priority_bucket"],
                "reason": eval_res["reason"],
                "explainability": eval_res["explainability"]
            })

        return results


hypothesis_engine = HypothesisEngine()

