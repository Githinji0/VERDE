import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.brain.simulation import simulation_orchestrator
from backend.app.database.models import AlphaCandidate, AlphaLineage, PreflightResult, ResearchScore, Simulation, SimulationMetric
from backend.app.database.session import get_db
from backend.app.generation.hypothesis_engine import hypothesis_engine
from backend.app.generation.preflight import preflight_engine
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash
from backend.app.research.optimization import candidate_optimizer, classify_candidate_tier

router = APIRouter(prefix="/api/candidates", tags=["Alpha Candidates"])


class CandidateGenerateRequest(BaseModel):
    family_code: str = Field(default="MOMENTUM")
    count: int = Field(default=5, ge=1, le=50)
    proven_ratio: float = Field(default=0.70)
    explored_ratio: float = Field(default=0.20)
    novel_ratio: float = Field(default=0.10)


class CandidateSimulateRequest(BaseModel):
    universe: str = Field(default="TOP3000")
    region: str = Field(default="USA")
    delay: int = Field(default=1)
    decay: int = Field(default=0)
    neutralization: str = Field(default="SUBINDUSTRY")
    truncation: float = Field(default=0.08)
    pasteurization: str = Field(default="ON")


@router.get("")
async def list_candidates(
    family: Optional[str] = None,
    tier: Optional[str] = None,
    preflight: Optional[str] = None,
    pareto_only: bool = False,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lists alpha candidates with optional filters."""
    query = select(AlphaCandidate).options(
        selectinload(AlphaCandidate.simulations).selectinload(Simulation.metrics),
        selectinload(AlphaCandidate.preflight_result),
        selectinload(AlphaCandidate.research_score)
    ).order_by(desc(AlphaCandidate.created_at)).offset(offset).limit(limit)

    if family:
        query = query.where(AlphaCandidate.family_code == family.upper())
    if tier:
        query = query.where(AlphaCandidate.tier == tier)
    if preflight:
        query = query.where(AlphaCandidate.preflight_status == preflight.upper())
    if pareto_only:
        query = query.where(AlphaCandidate.is_pareto == True)

    res = await db.execute(query)
    candidates = res.scalars().all()

    output = []
    for c in candidates:
        latest_sim = c.simulations[-1] if c.simulations else None
        latest_metric = latest_sim.metrics if (latest_sim and latest_sim.metrics) else None

        output.append({
            "id": c.id,
            "expression": c.expression,
            "family_code": c.family_code,
            "tier": c.tier,
            "preflight_status": c.preflight_status,
            "preflight_reason": c.preflight_reason,
            "complexity_score": c.complexity_score,
            "is_pareto": c.is_pareto,
            "pareto_rank": c.pareto_rank,
            "priority_bucket": c.priority_bucket,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "simulation_status": latest_sim.status if latest_sim else "UNSIMULATED",
            "sharpe": latest_metric.sharpe if (latest_metric and latest_metric.has_valid_metrics) else None,
            "fitness": latest_metric.fitness if (latest_metric and latest_metric.has_valid_metrics) else None,
            "turnover": latest_metric.turnover if (latest_metric and latest_metric.has_valid_metrics) else None,
            "margin_bps": latest_metric.margin_bps if (latest_metric and latest_metric.has_valid_metrics) else None,
            "has_valid_metrics": bool(latest_metric and latest_metric.has_valid_metrics)
        })

    return output


@router.get("/{candidate_id}")
async def get_candidate_details(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full candidate inspection details including AST, metrics, lineage, and diagnostics."""
    stmt = select(AlphaCandidate).where(AlphaCandidate.id == candidate_id).options(
        selectinload(AlphaCandidate.simulations).selectinload(Simulation.metrics),
        selectinload(AlphaCandidate.preflight_result),
        selectinload(AlphaCandidate.research_score),
        selectinload(AlphaCandidate.lineages)
    )
    res = await db.execute(stmt)
    c = res.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    sims_data = []
    for s in c.simulations:
        m = s.metrics
        sims_data.append({
            "id": s.id,
            "brain_sim_id": s.brain_sim_id,
            "status": s.status,
            "classification": s.classification,
            "portfolio_status": s.portfolio_status,
            "metrics_status": s.metrics_status,
            "sharpe": m.sharpe if m else None,
            "fitness": m.fitness if m else None,
            "turnover": m.turnover if m else None,
            "margin_bps": m.margin_bps if m else None,
            "returns_annualized": m.returns_annualized if m else None,
            "drawdown_max": m.drawdown_max if m else None,
            "diagnostic_reason": s.diagnostic_reason,
            "possible_cause": s.possible_cause,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        })

    lineages_data = []
    for l in c.lineages:
        lineages_data.append({
            "id": l.id,
            "parent_id": l.parent_id,
            "mutation_type": l.mutation_type,
            "changed_field": l.changed_field,
            "changed_operator": l.changed_operator,
            "changed_lookback": l.changed_lookback,
            "generation_reason": l.generation_reason,
            "created_at": l.created_at.isoformat() if l.created_at else None
        })

    return {
        "id": c.id,
        "expression": c.expression,
        "family_code": c.family_code,
        "tier": c.tier,
        "lifecycle_state": c.lifecycle_state,
        "experiment_id": c.experiment_id,
        "fields_used": c.fields_used,
        "operators_used": c.operators_used,
        "complexity_score": c.complexity_score,
        "compatibility_score": c.compatibility_score,
        "constant_signal_risk": c.constant_signal_risk,
        "validation_details": c.validation_details or {},
        "portfolio_telemetry": c.portfolio_telemetry or {},
        "redundancy_details": c.redundancy_details or {},
        "quality_breakdown": c.quality_breakdown or {},
        "is_pareto": c.is_pareto,
        "pareto_rank": c.pareto_rank,
        "preflight": {
            "decision": c.preflight_result.decision if c.preflight_result else c.preflight_status,
            "reason": c.preflight_result.reason if c.preflight_result else c.preflight_reason,
            "diagnostic_details": c.preflight_result.diagnostic_details if c.preflight_result else {}
        },
        "score": {
            "total_score": c.research_score.total_score if c.research_score else None,
            "is_target_passing": c.research_score.is_target_passing if c.research_score else False,
            "is_candidate_ready": c.research_score.is_candidate_ready if c.research_score else False
        } if c.research_score else None,
        "simulations": sims_data,
        "lineage": lineages_data,
        "created_at": c.created_at.isoformat() if c.created_at else None
    }


@router.post("/generate")
async def generate_candidates(req: CandidateGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Generates a batch of candidates for the given research family and runs preflight validation."""
    try:
        results = await hypothesis_engine.generate_and_preflight_candidates(
            family_code=req.family_code,
            count=req.count,
            proven_ratio=req.proven_ratio,
            explored_ratio=req.explored_ratio,
            novel_ratio=req.novel_ratio,
            session=db
        )
        return {"generated_count": len(results), "candidates": results}
    except Exception as e:
        from backend.app.core.logging import verde_logger
        verde_logger.log_event(
            event="CANDIDATE_GENERATION_FAILED",
            severity="ERROR",
            component="CANDIDATES_API",
            message=f"Candidate generation failed: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/{candidate_id}/validate")
async def validate_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Runs preflight validation on an existing candidate."""
    stmt = select(AlphaCandidate).where(AlphaCandidate.id == candidate_id)
    res = await db.execute(stmt)
    c = res.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")

    preflight = await preflight_engine.run_preflight(c.expression, c.family_code, db)
    
    c.preflight_status = preflight["decision"]
    c.preflight_reason = preflight["reason"]
    c.compatibility_score = preflight["compatibility_score"]
    c.constant_signal_risk = preflight["constant_signal_risk"]
    await db.commit()

    return preflight


@router.post("/{candidate_id}/simulate")
async def simulate_candidate(candidate_id: str, req: CandidateSimulateRequest, db: AsyncSession = Depends(get_db)):
    """Submits candidate to WorldQuant BRAIN for simulation."""
    sim = await simulation_orchestrator.execute_simulation(
        candidate_id=candidate_id,
        session=db,
        settings_dict=req.model_dump()
    )
    return {
        "simulation_id": sim.id,
        "candidate_id": sim.candidate_id,
        "status": sim.status,
        "brain_sim_id": sim.brain_sim_id,
        "classification": sim.classification,
        "message": f"Simulation initiated (Status: {sim.status})"
    }


@router.post("/{candidate_id}/mutate")
async def mutate_candidate(candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Generates targeted mutations for near-miss refinement, preflights them, and persists candidate records."""
    stmt = select(AlphaCandidate).where(AlphaCandidate.id == candidate_id)
    res = await db.execute(stmt)
    parent = res.scalar_one_or_none()

    if not parent:
        raise HTTPException(status_code=404, detail="Candidate not found")

    raw_mutations = candidate_optimizer.generate_mutations(parent.expression, parent.id)
    created_mutations = []

    for mut_item in raw_mutations:
        expr = mut_item["expression"]
        expr_hash = compute_expression_hash(expr)

        # Check if candidate with this expression already exists
        c_stmt = select(AlphaCandidate).where(AlphaCandidate.expression_hash == expr_hash)
        c_res = await db.execute(c_stmt)
        existing_c = c_res.scalar_one_or_none()

        if existing_c:
            cand = existing_c
        else:
            # Run preflight validation
            preflight = await preflight_engine.run_preflight(expr, parent.family_code, db)

            cand = AlphaCandidate(
                id=str(uuid.uuid4()),
                expression=expr,
                expression_hash=expr_hash,
                structure_hash=compute_structure_hash(expr),
                family_code=parent.family_code,
                parent_id=parent.id,
                mutation_type=mut_item.get("mutation_type"),
                generation_reason=mut_item.get("generation_reason"),
                tier="TIER_3_NEAR_MISS",
                preflight_status=preflight.get("decision", "PASS"),
                preflight_reason=preflight.get("reason", "Targeted hypothesis mutation"),
                complexity_score=preflight.get("complexity_score", 1.0),
                compatibility_score=preflight.get("compatibility_score", 1.0),
                constant_signal_risk=preflight.get("constant_signal_risk", 0.0),
                fields_used=list(preflight.get("fields_used", [])),
                operators_used=list(preflight.get("operators_used", [])),
                created_at=datetime.now(timezone.utc)
            )
            db.add(cand)

        created_mutations.append({
            "candidate_id": cand.id,
            "expression": cand.expression,
            "mutation_type": mut_item.get("mutation_type"),
            "preflight_status": cand.preflight_status,
            "generation_reason": mut_item.get("generation_reason"),
            "changed_lookback": mut_item.get("changed_lookback"),
            "changed_transformation": mut_item.get("changed_transformation"),
            "changed_group": mut_item.get("changed_group")
        })

    await db.commit()

    return {"parent_id": parent.id, "mutations": created_mutations}
