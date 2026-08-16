from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.brain.client import brain_client
from backend.app.brain.simulation import simulation_orchestrator
from backend.app.database.models import AlphaCandidate, Simulation, SimulationMetric
from backend.app.database.session import get_db

router = APIRouter(prefix="/api/simulations", tags=["Simulations"])


@router.get("")
async def list_simulations(
    status: Optional[str] = None,
    classification: Optional[str] = None,
    portfolio_status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lists simulations with pagination and status filters."""
    query = select(Simulation).options(
        selectinload(Simulation.candidate),
        selectinload(Simulation.metrics)
    ).order_by(desc(Simulation.created_at)).offset(offset).limit(limit)

    if status:
        query = query.where(Simulation.status == status.upper())
    if classification:
        query = query.where(Simulation.classification == classification.upper())
    if portfolio_status:
        query = query.where(Simulation.portfolio_status == portfolio_status.upper())

    res = await db.execute(query)
    sims = res.scalars().all()

    output = []
    for s in sims:
        m = s.metrics
        output.append({
            "id": s.id,
            "candidate_id": s.candidate_id,
            "brain_sim_id": s.brain_sim_id,
            "expression": s.candidate.expression if s.candidate else None,
            "family_code": s.candidate.family_code if s.candidate else None,
            "status": s.status,
            "classification": s.classification,
            "portfolio_status": s.portfolio_status,
            "metrics_status": s.metrics_status,
            "universe": s.universe,
            "region": s.region,
            "sharpe": m.sharpe if (m and m.has_valid_metrics) else None,
            "fitness": m.fitness if (m and m.has_valid_metrics) else None,
            "turnover": m.turnover if (m and m.has_valid_metrics) else None,
            "margin_bps": m.margin_bps if (m and m.has_valid_metrics) else None,
            "has_valid_metrics": bool(m and m.has_valid_metrics),
            "diagnostic_reason": s.diagnostic_reason,
            "possible_cause": s.possible_cause,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        })

    return output


@router.get("/{simulation_id}")
async def get_simulation_details(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full diagnostic details for a specific simulation."""
    stmt = select(Simulation).where(Simulation.id == simulation_id).options(
        selectinload(Simulation.candidate),
        selectinload(Simulation.metrics)
    )
    res = await db.execute(stmt)
    s = res.scalar_one_or_none()

    if not s:
        raise HTTPException(status_code=404, detail="Simulation not found")

    m = s.metrics
    return {
        "id": s.id,
        "candidate_id": s.candidate_id,
        "brain_sim_id": s.brain_sim_id,
        "expression": s.candidate.expression if s.candidate else None,
        "family_code": s.candidate.family_code if s.candidate else None,
        "status": s.status,
        "classification": s.classification,
        "portfolio_status": s.portfolio_status,
        "metrics_status": s.metrics_status,
        "universe": s.universe,
        "region": s.region,
        "delay": s.delay,
        "decay": s.decay,
        "neutralization": s.neutralization,
        "truncation": s.truncation,
        "metrics": {
            "sharpe": m.sharpe if m else None,
            "fitness": m.fitness if m else None,
            "turnover": m.turnover if m else None,
            "margin_bps": m.margin_bps if m else None,
            "returns_annualized": m.returns_annualized if m else None,
            "drawdown_max": m.drawdown_max if m else None,
            "long_count": m.long_count if m else None,
            "short_count": m.short_count if m else None,
            "has_valid_metrics": m.has_valid_metrics if m else False
        } if m else None,
        "diagnostic_reason": s.diagnostic_reason,
        "possible_cause": s.possible_cause,
        "raw_response": s.raw_response,
        "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None
    }


@router.post("/{simulation_id}/poll")
async def poll_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Polls remote BRAIN API status and updates simulation state."""
    stmt = select(Simulation).where(Simulation.id == simulation_id)
    res = await db.execute(stmt)
    s = res.scalar_one_or_none()

    if not s:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if not s.brain_sim_id:
        return {"status": s.status, "message": "No BRAIN simulation ID attached to this record."}

    poll_result = await brain_client.poll_simulation_status(s.brain_sim_id)
    
    if poll_result["status_code"] == 200:
        data = poll_result.get("data", {})
        if data.get("status") in ("COMPLETE", "ERROR") or "records" in data or "stats" in data:
            await simulation_orchestrator.update_simulation_from_response(s, data, db)

    return {"simulation_id": s.id, "status": s.status, "classification": s.classification}
