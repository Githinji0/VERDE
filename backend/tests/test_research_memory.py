import pytest
from sqlalchemy import select
from backend.app.database.models import AlphaCandidate, FamilyPerformance, FieldPerformance, Simulation, SimulationMetric
from backend.app.database.session import AsyncSessionFactory, init_db
from backend.app.research.memory import research_memory


@pytest.mark.asyncio
async def test_research_memory_updates_isolated_from_technical_failure():
    import uuid
    test_family = f"FAM_{uuid.uuid4().hex[:6]}"
    await init_db()
    async with AsyncSessionFactory() as session:
        cand = AlphaCandidate(
            expression="rank(close)",
            expression_hash=f"hash_test_{uuid.uuid4().hex[:6]}",
            structure_hash="struct_test_123",
            family_code=test_family,
            fields_used=["close"],
            operators_used=["rank"]
        )
        session.add(cand)
        await session.flush()

        # 1. Technical failure simulation (Empty portfolio)
        sim_tech = Simulation(
            candidate_id=cand.id,
            status="PORTFOLIO_EMPTY",
            classification="TECHNICAL_FAILURE",
            portfolio_status="EMPTY",
            metrics_status="MISSING"
        )
        session.add(sim_tech)
        await session.flush()

        # Update memory for technical failure
        await research_memory.update_memory_from_simulation(session, cand, sim_tech, None)

        # Verify: empty portfolio count incremented, but avg_sharpe is NOT set to 0
        fam_stmt = select(FamilyPerformance).where(FamilyPerformance.family_code == test_family)
        res = await session.execute(fam_stmt)
        fam = res.scalar_one()

        assert fam.total_candidates >= 1
        assert fam.empty_portfolio_count >= 1
        # Avg Sharpe remains None / unpolluted by technical failures!
        assert fam.avg_sharpe is None

        # 2. Valid simulation with Sharpe 1.50
        sim_valid = Simulation(
            candidate_id=cand.id,
            status="COMPLETE",
            classification="VALID_METRICS",
            portfolio_status="VALID",
            metrics_status="AVAILABLE"
        )
        session.add(sim_valid)
        await session.flush()

        metric_valid = SimulationMetric(
            simulation_id=sim_valid.id,
            sharpe=1.50,
            fitness=1.20,
            turnover=0.35,
            margin_bps=5.0,
            has_valid_metrics=True
        )
        session.add(metric_valid)
        await session.flush()

        await research_memory.update_memory_from_simulation(session, cand, sim_valid, metric_valid)

        res = await session.execute(fam_stmt)
        fam = res.scalar_one()
        assert fam.valid_simulations >= 1
        assert fam.avg_sharpe == 1.50
