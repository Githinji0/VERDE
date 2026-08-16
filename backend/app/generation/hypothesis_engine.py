import random
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import AlphaCandidate, PreflightResult
from backend.app.generation.family_info import RESEARCH_FAMILIES
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.preflight import preflight_engine
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash


class HypothesisEngine:
    """Generates hypothesis-driven alpha candidate expressions based on research families and priority buckets."""

    def __init__(self):
        self.families = RESEARCH_FAMILIES

    def generate_candidate_expression(
        self,
        family_code: str,
        priority_bucket: str = "PROVEN"
    ) -> Dict[str, Any]:
        """
        Synthesizes a candidate expression for a specific family and priority allocation.
        PROVEN: High-probability historically stable templates.
        EXPLORED: Variations with alternative lookbacks, normalizations, and field substitutions.
        NOVEL: Cross-family composites and orthogonal combinations.
        """
        family = self.families.get(family_code, self.families["MOMENTUM"])
        templates = family.get("templates", [])
        
        if not templates:
            templates = ["rank(close / ts_delay(close, 20) - 1)"]

        # Select template base
        template = random.choice(templates)
        
        # Select lookback suitable for family temporal behavior
        if family["temporal_behavior"] == "FAST":
            lookbacks = [3, 5, 10, 15, 20]
        elif family["temporal_behavior"] == "SLOW":
            lookbacks = [63, 126, 252]
        else:
            lookbacks = [10, 20, 30, 40, 60]

        lookback = random.choice(lookbacks)
        
        # Format expression template
        expr = template.replace("{lookback}", str(lookback))
        
        # In EXPLORED mode, introduce safe transformations (e.g. volatility normalization, smoothing)
        if priority_bucket == "EXPLORED":
            if random.random() > 0.5:
                expr = f"rank({expr} / (ts_std_dev(returns, 20) + 0.0001))"
            else:
                expr = f"ts_mean({expr}, 5)"
        elif priority_bucket == "NOVEL":
            # Cross-factor composite pairing
            expr = f"group_neutralize(0.5 * {expr} + 0.5 * rank(book_value / (close * shares_out + 0.0001)), subindustry)"

        return {
            "expression": expr,
            "family_code": family["code"],
            "hypothesis": family["core_hypothesis"],
            "priority_bucket": priority_bucket,
            "lookback": lookback
        }

    async def generate_and_preflight_candidates(
        self,
        family_code: str,
        count: int = 5,
        proven_ratio: float = 0.70,
        explored_ratio: float = 0.20,
        novel_ratio: float = 0.10,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """Generates a batch of candidates, runs preflight validation, and optionally persists valid records."""
        results = []
        
        for _ in range(count):
            # Sample priority bucket according to ratios
            r = random.random()
            if r < proven_ratio:
                bucket = "PROVEN"
            elif r < (proven_ratio + explored_ratio):
                bucket = "EXPLORED"
            else:
                bucket = "NOVEL"

            cand_data = self.generate_candidate_expression(family_code, bucket)
            expr = cand_data["expression"]
            
            # Run Preflight
            preflight = await preflight_engine.run_preflight(expr, family_code, session)
            
            # If DB session is provided, save candidate
            cand_id = None
            if session:
                expr_hash = compute_expression_hash(expr)
                struct_hash = compute_structure_hash(expr)
                
                tier = "TIER_1_PREFLIGHT_REJECTED" if preflight["decision"] == "REJECT" else "TIER_4_PROMISING"
                
                candidate = AlphaCandidate(
                    expression=expr,
                    expression_hash=expr_hash,
                    structure_hash=struct_hash,
                    family_code=family_code,
                    fields_used=preflight["fields_used"],
                    operators_used=preflight["operators_used"],
                    complexity_score=preflight["complexity_score"],
                    preflight_status=preflight["decision"],
                    preflight_reason=preflight["reason"],
                    compatibility_score=preflight["compatibility_score"],
                    constant_signal_risk=preflight["constant_signal_risk"],
                    tier=tier,
                    priority_bucket=bucket,
                    generation_reason=f"Generated via {bucket} allocation for {family_code} family."
                )
                session.add(candidate)
                await session.flush()
                cand_id = candidate.id

                preflight_rec = PreflightResult(
                    candidate_id=candidate.id,
                    decision=preflight["decision"],
                    reason=preflight["reason"],
                    compatibility_score=preflight["compatibility_score"],
                    constant_signal_risk=preflight["constant_signal_risk"],
                    complexity_score=preflight["complexity_score"],
                    diagnostic_details=preflight["diagnostic_details"]
                )
                session.add(preflight_rec)
                await session.commit()
                await session.refresh(candidate)

            results.append({
                "id": cand_id,
                "expression": expr,
                "family_code": family_code,
                "hypothesis": cand_data["hypothesis"],
                "priority_bucket": bucket,
                "preflight": preflight
            })

        return results


hypothesis_engine = HypothesisEngine()
