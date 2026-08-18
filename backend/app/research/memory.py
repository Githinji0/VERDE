from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.models import (
    AlphaCandidate, FamilyPerformance, FieldPerformance, OperatorPerformance, Simulation, SimulationMetric
)


class ResearchMemoryEngine:
    """
    Tracks empirical historical performance by Family, Field, and Operator.
    Drives adaptive generation feedback loops.
    Strictly isolates technical failures from Sharpe/Fitness averages.
    """

    @staticmethod
    async def update_memory_from_simulation(
        session: AsyncSession,
        candidate: AlphaCandidate,
        simulation: Simulation,
        metric: Optional[SimulationMetric]
    ):
        """Updates persistent performance matrices following simulation completion."""
        is_tech_failure = (simulation.classification == "TECHNICAL_FAILURE")
        is_empty_port = (simulation.portfolio_status == "EMPTY")
        has_valid_metrics = (metric is not None and metric.has_valid_metrics)

        # 1. Update Family Performance
        family_stmt = select(FamilyPerformance).where(FamilyPerformance.family_code == candidate.family_code)
        f_res = await session.execute(family_stmt)
        family_perf = f_res.scalar_one_or_none()

        if not family_perf:
            family_perf = FamilyPerformance(
                family_code=candidate.family_code,
                total_candidates=0,
                valid_simulations=0,
                empty_portfolio_count=0
            )
            session.add(family_perf)

        family_perf.total_candidates = (family_perf.total_candidates or 0) + 1
        if is_empty_port:
            family_perf.empty_portfolio_count = (family_perf.empty_portfolio_count or 0) + 1
        if has_valid_metrics:
            family_perf.valid_simulations = (family_perf.valid_simulations or 0) + 1
            # Rolling average update for Sharpe
            if metric.sharpe is not None:
                if family_perf.avg_sharpe is None:
                    family_perf.avg_sharpe = metric.sharpe
                else:
                    family_perf.avg_sharpe = round((family_perf.avg_sharpe * (family_perf.valid_simulations - 1) + metric.sharpe) / family_perf.valid_simulations, 4)
            if metric.fitness is not None:
                if family_perf.avg_fitness is None:
                    family_perf.avg_fitness = metric.fitness
                else:
                    family_perf.avg_fitness = round((family_perf.avg_fitness * (family_perf.valid_simulations - 1) + metric.fitness) / family_perf.valid_simulations, 4)
            if metric.turnover is not None:
                if family_perf.avg_turnover is None:
                    family_perf.avg_turnover = metric.turnover
                else:
                    family_perf.avg_turnover = round((family_perf.avg_turnover * (family_perf.valid_simulations - 1) + metric.turnover) / family_perf.valid_simulations, 4)

        family_perf.empty_portfolio_rate = round((family_perf.empty_portfolio_count or 0) / family_perf.total_candidates, 4)
        family_perf.success_rate = round((family_perf.valid_simulations or 0) / family_perf.total_candidates, 4)

        # 2. Update Field Performance
        for field_name in (candidate.fields_used or []):
            field_stmt = select(FieldPerformance).where(FieldPerformance.field_name == field_name)
            field_res = await session.execute(field_stmt)
            field_perf = field_res.scalar_one_or_none()

            if not field_perf:
                field_perf = FieldPerformance(
                    field_name=field_name,
                    total_candidates=0,
                    valid_simulations=0,
                    empty_portfolio_count=0
                )
                session.add(field_perf)

            field_perf.total_candidates = (field_perf.total_candidates or 0) + 1
            if is_empty_port:
                field_perf.empty_portfolio_count = (field_perf.empty_portfolio_count or 0) + 1
            if has_valid_metrics:
                field_perf.valid_simulations = (field_perf.valid_simulations or 0) + 1
                if metric.sharpe is not None:
                    if field_perf.avg_sharpe is None:
                        field_perf.avg_sharpe = metric.sharpe
                    else:
                        field_perf.avg_sharpe = round((field_perf.avg_sharpe * (field_perf.valid_simulations - 1) + metric.sharpe) / field_perf.valid_simulations, 4)
                if metric.fitness is not None:
                    if field_perf.avg_fitness is None:
                        field_perf.avg_fitness = metric.fitness
                    else:
                        field_perf.avg_fitness = round((field_perf.avg_fitness * (field_perf.valid_simulations - 1) + metric.fitness) / field_perf.valid_simulations, 4)

            field_perf.empty_portfolio_rate = round((field_perf.empty_portfolio_count or 0) / field_perf.total_candidates, 4)
            field_perf.success_rate = round((field_perf.valid_simulations or 0) / field_perf.total_candidates, 4)

        # 3. Update Operator Performance
        for op_name in (candidate.operators_used or []):
            op_stmt = select(OperatorPerformance).where(OperatorPerformance.operator_name == op_name)
            op_res = await session.execute(op_stmt)
            op_perf = op_res.scalar_one_or_none()

            if not op_perf:
                op_perf = OperatorPerformance(
                    operator_name=op_name,
                    total_candidates=0,
                    valid_simulations=0,
                    empty_portfolio_count=0
                )
                session.add(op_perf)

            op_perf.total_candidates = (op_perf.total_candidates or 0) + 1
            if is_empty_port:
                op_perf.empty_portfolio_count = (op_perf.empty_portfolio_count or 0) + 1
            if has_valid_metrics:
                op_perf.valid_simulations = (op_perf.valid_simulations or 0) + 1
                if metric.sharpe is not None:
                    if op_perf.avg_sharpe is None:
                        op_perf.avg_sharpe = metric.sharpe
                    else:
                        op_perf.avg_sharpe = round((op_perf.avg_sharpe * (op_perf.valid_simulations - 1) + metric.sharpe) / op_perf.valid_simulations, 4)
                if metric.fitness is not None:
                    if op_perf.avg_fitness is None:
                        op_perf.avg_fitness = metric.fitness
                    else:
                        op_perf.avg_fitness = round((op_perf.avg_fitness * (op_perf.valid_simulations - 1) + metric.fitness) / op_perf.valid_simulations, 4)

            op_perf.empty_portfolio_rate = round((op_perf.empty_portfolio_count or 0) / op_perf.total_candidates, 4)
            op_perf.success_rate = round((op_perf.valid_simulations or 0) / op_perf.total_candidates, 4)

        await session.commit()

    @staticmethod
    async def detect_research_gaps(session: AsyncSession) -> Dict[str, Any]:
        """
        Analyzes the research database to discover underexplored families, field categories,
        and operator combinations to guide intelligent research exploration.
        """
        fam_stmt = select(FamilyPerformance)
        fam_res = await session.execute(fam_stmt)
        family_perfs = fam_res.scalars().all()

        underexplored_families = []
        for fp in family_perfs:
            if (fp.total_candidates or 0) < 5:
                underexplored_families.append({
                    "family_code": fp.family_code,
                    "tested_candidates": fp.total_candidates or 0,
                    "reason": f"Only {fp.total_candidates or 0} candidates explored."
                })

        field_stmt = select(FieldPerformance)
        field_res = await session.execute(field_stmt)
        field_perfs = field_res.scalars().all()

        underexplored_fields = [fp.field_name for fp in field_perfs if (fp.total_candidates or 0) < 3]

        return {
            "underexplored_families": underexplored_families,
            "underexplored_fields": underexplored_fields,
            "recommended_budget_allocation": {
                "exploration_rate": 0.40 if underexplored_families else 0.20,
                "exploitation_rate": 0.60 if underexplored_families else 0.80
            }
        }

    @staticmethod
    async def get_evidence_weighted_memory(session: AsyncSession, min_samples: int = 3) -> Dict[str, Any]:
        """
        Returns evidence-weighted performance statistics, filtering out unconfident single-sample spikes.
        """
        fam_stmt = select(FamilyPerformance).where(FamilyPerformance.total_candidates >= min_samples)
        fam_res = await session.execute(fam_stmt)
        top_families = sorted(fam_res.scalars().all(), key=lambda f: f.avg_sharpe or 0.0, reverse=True)

        return {
            "top_families": [
                {
                    "family_code": f.family_code,
                    "avg_sharpe": f.avg_sharpe,
                    "avg_fitness": f.avg_fitness,
                    "success_rate": f.success_rate,
                    "total_candidates": f.total_candidates
                } for f in top_families
            ]
        }


research_memory = ResearchMemoryEngine()

