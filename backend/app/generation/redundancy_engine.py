"""
Redundancy Engine for VERDE Alpha Research Platform.
Detects exact duplicates, structural AST duplicates, operator-pattern overlaps,
and signal redundancy before candidate promotion.
"""

from typing import Dict, Any, List, Optional
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database.models import AlphaCandidate


class RedundancyEngine:
    """
    Evaluates candidate expressions for redundancy against historical research memory
    and existing candidate database.
    """

    async def evaluate_redundancy(
        self,
        expression: str,
        structure_hash: str,
        fields_used: List[str],
        operators_used: List[str],
        family_code: str,
        current_candidate_id: Optional[str],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Executes multi-tier redundancy check:
        1. Exact expression match
        2. Structural tree match (same AST topology and operators)
        3. High feature/operator overlap within same family
        """
        normalized_expr = "".join(expression.split()).lower()
        expr_hash = hashlib.sha256(normalized_expr.encode('utf-8')).hexdigest()

        reasons = []
        is_duplicate = False
        duplicate_type = None
        duplicate_of_id = None
        similarity_score = 0.0
        correlation_score = 0.0

        # Query existing candidates excluding current candidate
        stmt = select(AlphaCandidate)
        if current_candidate_id:
            stmt = stmt.where(AlphaCandidate.id != current_candidate_id)
        
        res = await session.execute(stmt)
        existing_cands = res.scalars().all()

        for past_cand in existing_cands:
            past_norm = "".join(past_cand.expression.split()).lower()
            
            # 1. Exact Match Check
            if past_norm == normalized_expr or past_cand.expression_hash == expr_hash:
                is_duplicate = True
                duplicate_type = "EXACT_DUPLICATE"
                duplicate_of_id = past_cand.id
                similarity_score = 1.0
                correlation_score = 1.0
                reasons.append(f"Exact expression match with candidate {past_cand.id[:8]}")
                break

            # 2. Structural Match Check
            if past_cand.structure_hash == structure_hash and past_cand.family_code == family_code:
                # Check operator and field overlap ratio
                past_fields = set(past_cand.fields_used or [])
                curr_fields = set(fields_used or [])
                field_jaccard = (
                    len(curr_fields.intersection(past_fields)) / max(len(curr_fields.union(past_fields)), 1)
                )

                if field_jaccard >= 0.8:
                    is_duplicate = True
                    duplicate_type = "STRUCTURAL_DUPLICATE"
                    duplicate_of_id = past_cand.id
                    similarity_score = round(0.85 + (0.15 * field_jaccard), 2)
                    correlation_score = round(0.80 + (0.15 * field_jaccard), 2)
                    reasons.append(
                        f"Structural AST duplicate with candidate {past_cand.id[:8]} "
                        f"(Field Jaccard similarity: {round(field_jaccard, 2)})"
                    )
                    break

            # 3. High Correlation / Overlap Check
            if past_cand.family_code == family_code:
                past_ops = set(past_cand.operators_used or [])
                curr_ops = set(operators_used or [])
                op_jaccard = (
                    len(curr_ops.intersection(past_ops)) / max(len(curr_ops.union(past_ops)), 1)
                ) if curr_ops and past_ops else 0.0

                past_fields = set(past_cand.fields_used or [])
                curr_fields = set(fields_used or [])
                field_jaccard = (
                    len(curr_fields.intersection(past_fields)) / max(len(curr_fields.union(past_fields)), 1)
                ) if curr_fields and past_fields else 0.0

                combined_sim = (0.5 * op_jaccard) + (0.5 * field_jaccard)
                if combined_sim > similarity_score:
                    similarity_score = round(combined_sim, 2)
                    correlation_score = round(combined_sim * 0.9, 2)

                if combined_sim >= 0.90:
                    is_duplicate = True
                    duplicate_type = "HIGH_SIGNAL_REDUNDANCY"
                    duplicate_of_id = past_cand.id
                    reasons.append(
                        f"High signal redundancy with candidate {past_cand.id[:8]} "
                        f"(Combined similarity: {round(combined_sim, 2)})"
                    )
                    break

        if not is_duplicate:
            if similarity_score < 0.3:
                reasons.append("Novel alpha expression structure and field combination.")
            else:
                reasons.append(f"Acceptable novelty (Max similarity: {similarity_score}).")

        return {
            "is_duplicate": is_duplicate,
            "duplicate_type": duplicate_type,
            "duplicate_of_id": duplicate_of_id,
            "similarity_score": similarity_score,
            "correlation_score": correlation_score,
            "reasons": reasons
        }


redundancy_engine = RedundancyEngine()
