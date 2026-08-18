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
        Analyzes research experiments & historical candidate evidence to identify
        meaningful research gaps (underexplored + high potential + insufficient evidence)
        and calculate evidence-driven budget allocations across families.
        """
        from backend.app.database.models import ResearchExperiment, AlphaCandidate, ResearchFamily

        # Query all active families
        fam_stmt = select(ResearchFamily).where(ResearchFamily.is_active == True)
        families = (await session.execute(fam_stmt)).scalars().all()

        underexplored_gaps = []
        family_allocations = {}
        total_weight = 0.0

        for fam in families:
            f_code = fam.code

            # Gather experiment counts for this family
            exp_stmt = select(ResearchExperiment).where(ResearchExperiment.family_code == f_code)
            exps = (await session.execute(exp_stmt)).scalars().all()
            exp_count = len(exps)

            # Gather candidate stats
            cand_stmt = select(AlphaCandidate).where(AlphaCandidate.family_code == f_code)
            cands = (await session.execute(cand_stmt)).scalars().all()

            tot_cands = len(cands)
            eval_cands = [c for c in cands if c.lifecycle_state in ["EVALUATED", "PROMISING", "ELITE", "SUBMITTED", "PORTFOLIO_EMPTY", "REJECTED"]]
            evaluated_count = len(eval_cands)
            elite_count = len([c for c in cands if c.lifecycle_state in ["ELITE", "SUBMITTED"]])
            promising_count = len([c for c in cands if c.lifecycle_state == "PROMISING"])
            rejected_count = len([c for c in cands if c.lifecycle_state in ["REJECTED", "PORTFOLIO_EMPTY", "INVALID"]])

            qualities = [c.alpha_quality_score for c in cands if c.alpha_quality_score is not None]
            avg_quality = round(sum(qualities) / len(qualities), 2) if qualities else 0.0

            # Gap Criteria: Underexplored OR (High Promising Rate + Low Experiments)
            coverage = "LOW" if exp_count < 2 or evaluated_count < 10 else ("MEDIUM" if exp_count < 5 else "HIGH")
            potential = "UNKNOWN" if evaluated_count < 5 else ("HIGH" if elite_count > 0 or promising_count > 2 else ("MODERATE" if avg_quality > 40 else "LOW"))

            if coverage in ["LOW", "MEDIUM"] or (potential == "HIGH" and coverage != "HIGH"):
                underexplored_gaps.append({
                    "family_code": f_code,
                    "family_name": fam.name,
                    "experiments_count": exp_count,
                    "candidates_generated": tot_cands,
                    "candidates_evaluated": evaluated_count,
                    "rejected_count": rejected_count,
                    "promising_count": promising_count,
                    "elite_count": elite_count,
                    "average_quality": avg_quality,
                    "coverage": coverage,
                    "potential": potential,
                    "recommendation": f"Explore {f_code} using {fam.core_hypothesis}"
                })

            # Calculate allocation weight
            # Base weight: 20.0
            # Higher for underexplored with potential, lower for heavily explored low-quality
            base_w = 25.0
            if coverage == "LOW": base_w += 15.0
            if potential == "HIGH": base_w += 20.0
            if potential == "LOW" and coverage == "HIGH": base_w = max(5.0, base_w - 15.0)

            family_allocations[f_code] = base_w
            total_weight += base_w

        # Normalize allocations to 100%
        normalized_allocations = {}
        for f_code, w in family_allocations.items():
            pct = round((w / total_weight) * 100.0, 1) if total_weight > 0 else 0.0
            normalized_allocations[f_code] = f"{pct}%"

        return {
            "underexplored_gaps": underexplored_gaps,
            "research_allocation": normalized_allocations,
            "recommended_budget_allocation": {
                "exploration_rate": 0.40 if underexplored_gaps else 0.20,
                "exploitation_rate": 0.60 if underexplored_gaps else 0.80
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

