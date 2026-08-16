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
    # Reconcile any active running/submitting simulations before returning
    await simulation_orchestrator.reconcile_running_simulations(db)

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

    from backend.app.research.diagnostics import SimulationDiagnosticEngine

    m = s.metrics
    sanitized_raw = SimulationDiagnosticEngine.sanitize_telemetry(s.raw_response) if s.raw_response else None

    from backend.app.generation.ast_parser import ExpressionASTParser
    expr_str = s.candidate.expression if s.candidate else ""
    expr_hash = ExpressionASTParser.compute_expression_hash(expr_str) if expr_str else None
    root_node = ExpressionASTParser.parse(expr_str) if expr_str else None

    diag_details = s.diagnostic_details or {}
    comp_tests = diag_details.get("component_tests") or []

    expression_analysis = {
        "expression": expr_str,
        "expression_hash": expr_hash,
        "root": {
            "operator": root_node.name if root_node else "",
            "category": root_node.category() if root_node else ""
        },
        "components": comp_tests
    }

    return {
        "id": s.id,
        "candidate_id": s.candidate_id,
        "brain_sim_id": s.brain_sim_id,
        "expression": expr_str,
        "expression_hash": expr_hash,
        "expression_analysis": expression_analysis,
        "family_code": s.candidate.family_code if s.candidate else None,
        "status": s.status,
        "classification": s.classification,
        "portfolio_status": s.portfolio_status,
        "metrics_status": s.metrics_status,
        "remote_status": s.remote_status or s.status,
        "diagnostic_code": s.diagnostic_code or "NONE",
        "root_cause_type": s.root_cause_type,
        "root_cause_confidence": s.root_cause_confidence,
        "position_count": s.position_count,
        "why_not_proven": (s.diagnostic_details or {}).get("why_not_proven") or (s.diagnostic_details or {}).get("root_cause", {}).get("why_not_proven"),
        "diagnostic_details": s.diagnostic_details or {},
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
        "raw_response": sanitized_raw,
        "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None
    }


from backend.app.core.security import vault
from backend.app.database.models import AlphaCandidate, BrainConnection, BrainSession, Simulation, SimulationMetric


@router.post("/{simulation_id}/poll")
async def poll_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Polls remote BRAIN API status and updates simulation state."""
    await simulation_orchestrator.reconcile_running_simulations(db)

    stmt = select(Simulation).where(Simulation.id == simulation_id).options(
        selectinload(Simulation.candidate),
        selectinload(Simulation.metrics)
    )
    res = await db.execute(stmt)
    s = res.scalar_one_or_none()

    if not s:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if not s.brain_sim_id:
        return {"status": s.status, "message": "No BRAIN simulation ID attached to this record."}

    # Fetch cookies if available
    cookies = None
    conn_stmt = select(BrainConnection).where(BrainConnection.status == "CONNECTED", BrainConnection.is_active == True)
    conn_res = await db.execute(conn_stmt)
    brain_conn = conn_res.scalars().first()
    if brain_conn:
        sess_stmt = select(BrainSession).where(BrainSession.connection_id == brain_conn.id, BrainSession.is_valid == True)
        sess_res = await db.execute(sess_stmt)
        brain_sess = sess_res.scalars().first()
        if brain_sess and brain_sess.encrypted_session_cookie:
            try:
                import json
                cookie_str = vault.decrypt(brain_sess.encrypted_session_cookie)
                cookies = json.loads(cookie_str)
            except Exception:
                pass

    poll_result = await brain_client.poll_simulation_status(s.brain_sim_id, cookies=cookies)
    
    if poll_result.get("status_code") == 200:
        data = poll_result.get("data", {})
        if data.get("status") in ("COMPLETE", "ERROR", "CANCELLED") or "records" in data or "stats" in data:
            await simulation_orchestrator.update_simulation_from_response(s, data, db)

    m = s.metrics
    return {
        "simulation_id": s.id,
        "status": s.status,
        "classification": s.classification,
        "sharpe": m.sharpe if (m and m.has_valid_metrics) else None,
        "fitness": m.fitness if (m and m.has_valid_metrics) else None,
        "turnover": m.turnover if (m and m.has_valid_metrics) else None,
        "margin_bps": m.margin_bps if (m and m.has_valid_metrics) else None,
        "has_valid_metrics": bool(m and m.has_valid_metrics)
    }
