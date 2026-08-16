from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import AlphaCandidate, AlphaLineage


class LineageTracker:
    """Records parent-child alpha candidate relationships and mutation audit trails."""

    @staticmethod
    async def record_mutation(
        session: AsyncSession,
        candidate_id: str,
        parent_id: Optional[str],
        mutation_type: str,
        changed_field: Optional[str] = None,
        changed_operator: Optional[str] = None,
        changed_lookback: Optional[int] = None,
        changed_group: Optional[str] = None,
        changed_transformation: Optional[str] = None,
        generation_reason: Optional[str] = None
    ) -> AlphaLineage:
        lineage = AlphaLineage(
            candidate_id=candidate_id,
            parent_id=parent_id,
            mutation_type=mutation_type,
            changed_field=changed_field,
            changed_operator=changed_operator,
            changed_lookback=changed_lookback,
            changed_group=changed_group,
            changed_transformation=changed_transformation,
            generation_reason=generation_reason
        )
        session.add(lineage)
        await session.commit()
        return lineage


lineage_tracker = LineageTracker()
