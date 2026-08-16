from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.config import settings
from backend.app.database.models import (
    AlphaCandidate, BrainConnection, FamilyPerformance, FieldPerformance, OperatorPerformance,
    PreflightResult, ResearchLog, Simulation, SimulationMetric
)
from backend.app.database.session import get_db
from backend.app.workers.queue import job_queue

router = APIRouter(prefix="/api/analytics", tags=["Analytics & KPIs"])


@router.get("/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """Computes comprehensive dashboard KPIs without false-zero metric contamination."""
    # Total candidates
    cand_count_res = await db.execute(select(func.count(AlphaCandidate.id)))
    total_candidates = cand_count_res.scalar() or 0

    # Total simulations
    sim_count_res = await db.execute(select(func.count(Simulation.id)))
    total_simulations = sim_count_res.scalar() or 0

    # Valid simulations count
    valid_sim_res = await db.execute(
        select(func.count(SimulationMetric.id)).where(SimulationMetric.has_valid_metrics == True)
    )
    valid_simulations = valid_sim_res.scalar() or 0

    # Portfolio empty count
    empty_port_res = await db.execute(
        select(func.count(Simulation.id)).where(Simulation.portfolio_status == "EMPTY")
    )
    empty_port_count = empty_port_res.scalar() or 0
    portfolio_empty_rate = round(empty_port_count / total_simulations, 4) if total_simulations > 0 else 0.0

    # Metrics missing count
    metrics_miss_res = await db.execute(
        select(func.count(Simulation.id)).where(Simulation.metrics_status == "MISSING")
    )
    metrics_missing_count = metrics_miss_res.scalar() or 0
    metrics_missing_rate = round(metrics_missing_count / total_simulations, 4) if total_simulations > 0 else 0.0

    # Preflight rejection count
    preflight_reject_res = await db.execute(
        select(func.count(PreflightResult.id)).where(PreflightResult.decision == "REJECT")
    )
    preflight_rejects = preflight_reject_res.scalar() or 0
    preflight_rejection_rate = round(preflight_rejects / total_candidates, 4) if total_candidates > 0 else 0.0

    # Average metrics strictly computed over valid simulations only
    avg_metrics_stmt = select(
        func.avg(SimulationMetric.sharpe),
        func.avg(SimulationMetric.fitness),
        func.avg(SimulationMetric.turnover),
        func.avg(SimulationMetric.margin_bps)
    ).where(SimulationMetric.has_valid_metrics == True)
    avg_res = await db.execute(avg_metrics_stmt)
    avg_sharpe, avg_fitness, avg_turnover, avg_margin = avg_res.first()

    # Pareto count
    pareto_res = await db.execute(select(func.count(AlphaCandidate.id)).where(AlphaCandidate.is_pareto == True))
    pareto_count = pareto_res.scalar() or 0

    # Near threshold candidates count
    near_miss_res = await db.execute(select(func.count(AlphaCandidate.id)).where(AlphaCandidate.tier == "TIER_3_NEAR_MISS"))
    near_miss_count = near_miss_res.scalar() or 0

    # Best candidate
    best_cand_stmt = select(AlphaCandidate).join(Simulation).join(SimulationMetric).where(
        SimulationMetric.has_valid_metrics == True
    ).order_by(SimulationMetric.sharpe.desc()).limit(1).options(
        selectinload(AlphaCandidate.simulations).selectinload(Simulation.metrics)
    )
    best_cand_res = await db.execute(best_cand_stmt)
    best_cand = best_cand_res.scalar_one_or_none()

    best_candidate_data = None
    if best_cand and best_cand.simulations and best_cand.simulations[-1].metrics:
        bm = best_cand.simulations[-1].metrics
        best_candidate_data = {
            "id": best_cand.id,
            "expression": best_cand.expression,
            "family_code": best_cand.family_code,
            "sharpe": bm.sharpe,
            "fitness": bm.fitness,
            "turnover": bm.turnover,
            "margin_bps": bm.margin_bps
        }

    # BRAIN connection status
    conn_stmt = select(BrainConnection).where(BrainConnection.is_active == True)
    conn_res = await db.execute(conn_stmt)
    conn = conn_res.scalars().first()

    # Last error log
    last_err_stmt = select(ResearchLog).where(ResearchLog.severity.in_(["WARNING", "ERROR", "CRITICAL"])).order_by(ResearchLog.timestamp.desc()).limit(1)
    err_res = await db.execute(last_err_stmt)
    last_err = err_res.scalar_one_or_none()

    return {
        "kpis": {
            "total_candidates": total_candidates,
            "total_simulations": total_simulations,
            "valid_simulations": valid_simulations,
            "portfolio_empty_rate": portfolio_empty_rate,
            "metrics_missing_rate": metrics_missing_rate,
            "preflight_rejection_rate": preflight_rejection_rate,
            "avg_sharpe": round(avg_sharpe, 3) if avg_sharpe is not None else None,
            "avg_fitness": round(avg_fitness, 3) if avg_fitness is not None else None,
            "avg_turnover": round(avg_turnover, 3) if avg_turnover is not None else None,
            "avg_margin_bps": round(avg_margin, 2) if avg_margin is not None else None,
            "pareto_candidates": pareto_count,
            "candidates_near_threshold": near_miss_count,
            "best_current_candidate": best_candidate_data
        },
        "system_status": {
            "brain_connection": conn.status if conn else "DISCONNECTED",
            "worker_status": "IDLE",
            "queue_size": job_queue.get_queue_size(),
            "ai_status": "ENABLED" if settings.AI_ENABLED else "DISABLED",
            "last_error": {
                "event": last_err.event,
                "message": last_err.message,
                "timestamp": last_err.timestamp.isoformat()
            } if last_err else None
        }
    }


@router.get("/pareto")
async def get_pareto_scatter_data(db: AsyncSession = Depends(get_db)):
    """Returns Sharpe vs Turnover vs Fitness dataset for Pareto visualization."""
    stmt = select(AlphaCandidate).options(
        selectinload(AlphaCandidate.simulations).selectinload(Simulation.metrics)
    ).where(AlphaCandidate.simulations.any())
    res = await db.execute(stmt)
    candidates = res.scalars().all()

    points = []
    for c in candidates:
        for s in c.simulations:
            if s.metrics and s.metrics.has_valid_metrics:
                m = s.metrics
                points.append({
                    "id": c.id,
                    "expression": c.expression,
                    "family_code": c.family_code,
                    "tier": c.tier,
                    "is_pareto": c.is_pareto,
                    "sharpe": m.sharpe,
                    "fitness": m.fitness,
                    "turnover": m.turnover,
                    "margin_bps": m.margin_bps
                })

    return {"points": points}


@router.get("/families")
async def get_family_performance_data(db: AsyncSession = Depends(get_db)):
    """Returns performance breakdown aggregated by research family."""
    stmt = select(FamilyPerformance).order_by(FamilyPerformance.total_candidates.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/fields")
async def get_field_performance_data(db: AsyncSession = Depends(get_db)):
    """Returns performance and empty-portfolio statistics by field."""
    stmt = select(FieldPerformance).order_by(FieldPerformance.total_candidates.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/operators")
async def get_operator_performance_data(db: AsyncSession = Depends(get_db)):
    """Returns performance and empty-portfolio statistics by operator."""
    stmt = select(OperatorPerformance).order_by(OperatorPerformance.total_candidates.desc())
    res = await db.execute(stmt)
    return res.scalars().all()
