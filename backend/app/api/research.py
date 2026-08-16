from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import AlphaCandidate, AlphaLineage, FamilyPerformance, FieldPerformance, OperatorPerformance
from backend.app.database.session import get_db
from backend.app.generation.family_info import RESEARCH_FAMILIES
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.operator_registry import OPERATOR_REGISTRY

router = APIRouter(prefix="/api/research", tags=["Research Families & Memory"])


@router.get("/families")
async def list_research_families():
    """Returns registry of all 17+ quantitative research families and their hypotheses."""
    return list(RESEARCH_FAMILIES.values())


@router.get("/families/{family_code}")
async def get_research_family_details(family_code: str):
    """Returns detailed specification for a given research family."""
    code = family_code.upper().strip()
    family = RESEARCH_FAMILIES.get(code)
    if not family:
        raise HTTPException(status_code=404, detail=f"Research family '{family_code}' not found.")
    return family


@router.get("/fields")
async def list_registered_fields():
    """Returns field registry with temporal frequency ratings and categories."""
    return list(FIELD_REGISTRY.values())


@router.get("/operators")
async def list_registered_operators():
    """Returns operator registry with arity and complexity costs."""
    return list(OPERATOR_REGISTRY.values())


@router.get("/memory")
async def get_research_memory_overview(db: AsyncSession = Depends(get_db)):
    """Returns empirical performance summary across families, fields, and operators."""
    fam_res = await db.execute(select(FamilyPerformance).order_by(FamilyPerformance.total_candidates.desc()))
    field_res = await db.execute(select(FieldPerformance).order_by(FieldPerformance.total_candidates.desc()))
    op_res = await db.execute(select(OperatorPerformance).order_by(OperatorPerformance.total_candidates.desc()))

    return {
        "families": fam_res.scalars().all(),
        "fields": field_res.scalars().all(),
        "operators": op_res.scalars().all()
    }


@router.get("/lineage/{candidate_id}")
async def get_candidate_lineage_tree(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full parent-child ancestor tree for an alpha candidate."""
    stmt = select(AlphaLineage).where(AlphaLineage.candidate_id == candidate_id)
    res = await db.execute(stmt)
    return res.scalars().all()
