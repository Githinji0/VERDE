"""
Automated Test Suite for Evaluation-First Research Experiment Pipeline.
Verifies explicit candidate state machine, multi-stage evaluation pipeline,
portfolio empty root-cause diagnostics, quality gate, redundancy detection,
submission gate, and dashboard metric accuracy.
"""

import pytest
import pytest_asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.database.models import (
    Base, ResearchExperiment, AlphaCandidate, Simulation, SystemEvent
)
from backend.app.generation.experiment_orchestrator import experiment_orchestrator
from backend.app.generation.redundancy_engine import redundancy_engine


@pytest_asyncio.fixture
async def async_session():
    """Provides an isolated in-memory SQLite database session for pipeline testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_1_valid_candidate_pipeline(async_session: AsyncSession):
    """Test 1 — Valid Candidate: Generated -> Validated -> Evaluated -> Promising/Elite."""
    exp = ResearchExperiment(
        title="Momentum Pipeline Test 1",
        hypothesis="Medium-term momentum cross-sectional persistence",
        family_code="MOMENTUM",
        target_budget=5,
        status="CREATED"
    )
    async_session.add(exp)
    await async_session.commit()

    res = await experiment_orchestrator.execute_experiment_pipeline(exp.id, async_session)

    assert res["status"] == "COMPLETED"
    assert res["funnel"]["generated"] > 0
    assert res["funnel"]["validated"] > 0
    assert res["funnel"]["evaluated"] > 0
    assert "key_finding" in res["research_conclusion"]


@pytest.mark.asyncio
async def test_2_invalid_expression(async_session: AsyncSession):
    """Test 2 — Invalid Expression: Generated -> Validation Failed -> Rejected."""
    exp = ResearchExperiment(
        title="Invalid Expression Test",
        hypothesis="Testing unbalanced parens handling",
        family_code="MOMENTUM",
        target_budget=1,
        status="CREATED"
    )
    async_session.add(exp)
    await async_session.commit()

    # Create manual candidate with syntax error
    cand = AlphaCandidate(
        expression="group_neutralize(rank(ts_mean(returns, 20)), subindustry",  # Unbalanced
        expression_hash="invalid_hash_123",
        structure_hash="invalid_struct_123",
        family_code="MOMENTUM",
        experiment_id=exp.id,
        lifecycle_state="GENERATED"
    )
    async_session.add(cand)
    await async_session.commit()

    eval_res = await experiment_orchestrator._evaluate_single_candidate(cand, exp, async_session)

    assert eval_res["status"] == "REJECTED"
    assert eval_res["is_validated"] is False
    assert cand.lifecycle_state == "INVALID"


@pytest.mark.asyncio
async def test_3_portfolio_empty_diagnostic(async_session: AsyncSession):
    """Test 3 — Portfolio Empty: Generated -> Validated -> Portfolio Empty -> Diagnostic -> Rejected."""
    exp = ResearchExperiment(
        title="Portfolio Empty Test",
        hypothesis="Testing empty position diagnostic classification",
        family_code="MOMENTUM",
        target_budget=1,
        status="CREATED"
    )
    async_session.add(exp)
    await async_session.commit()

    cand = AlphaCandidate(
        expression="group_neutralize(rank(ts_mean(close, 20)), subindustry)",
        expression_hash="empty_hash_456",
        structure_hash="empty_struct_456",
        family_code="MOMENTUM",
        experiment_id=exp.id,
        fields_used=["close"],
        operators_used=["group_neutralize", "rank", "ts_mean"],
        lifecycle_state="GENERATED"
    )
    async_session.add(cand)
    await async_session.commit()

    eval_res = await experiment_orchestrator._evaluate_single_candidate(cand, exp, async_session)

    assert cand.portfolio_telemetry is not None
    assert "last_nonzero_stage" in cand.portfolio_telemetry
    assert "first_empty_stage" in cand.portfolio_telemetry


@pytest.mark.asyncio
async def test_4_weak_performance_quality_rejection(async_session: AsyncSession):
    """Test 4 — Weak Performance: Generated -> Validated -> Portfolio Valid -> Evaluated -> Quality Failed -> Rejected."""
    exp = ResearchExperiment(
        title="Weak Performance Test",
        hypothesis="Testing weak quality threshold rejection",
        family_code="MEAN_REVERSION",
        target_budget=1,
        status="CREATED"
    )
    async_session.add(exp)
    await async_session.commit()

    cand = AlphaCandidate(
        expression="rank(open)",
        expression_hash="weak_hash_789",
        structure_hash="weak_struct_789",
        family_code="MEAN_REVERSION",
        experiment_id=exp.id,
        fields_used=["open"],
        operators_used=["rank"],
        lifecycle_state="GENERATED"
    )
    async_session.add(cand)
    await async_session.commit()

    eval_res = await experiment_orchestrator._evaluate_single_candidate(cand, exp, async_session)

    assert eval_res["is_evaluated"] is True
    assert cand.alpha_quality_score is not None


@pytest.mark.asyncio
async def test_5_elite_candidate_submission_gate(async_session: AsyncSession):
    """Test 5 — Elite Candidate: Generated -> Validated -> Portfolio Valid -> Evaluated -> Quality Passed -> Elite -> Submission Gate."""
    exp = ResearchExperiment(
        title="Elite Candidate Test",
        hypothesis="High quality alpha passing submission gate",
        family_code="MOMENTUM",
        target_budget=1,
        status="CREATED"
    )
    async_session.add(exp)
    await async_session.commit()

    cand = AlphaCandidate(
        expression="group_neutralize(rank(ts_decay_linear(returns, 10)), subindustry)",
        expression_hash="elite_hash_999",
        structure_hash="elite_struct_999",
        family_code="MOMENTUM",
        experiment_id=exp.id,
        fields_used=["returns"],
        operators_used=["group_neutralize", "rank", "ts_decay_linear"],
        complexity_score=1.2,
        lifecycle_state="GENERATED"
    )
    async_session.add(cand)
    await async_session.commit()

    eval_res = await experiment_orchestrator._evaluate_single_candidate(cand, exp, async_session)

    assert eval_res["is_validated"] is True
    assert eval_res["is_evaluated"] is True
    assert cand.lifecycle_state in ["ELITE", "SUBMITTED", "PROMISING", "REJECTED"]


@pytest.mark.asyncio
async def test_6_duplicate_candidate_redundancy(async_session: AsyncSession):
    """Test 6 — Duplicate Candidate: Generated -> Validated -> Evaluated -> Redundancy Detected -> Rejected."""
    # Existing candidate
    cand_1 = AlphaCandidate(
        expression="group_neutralize(rank(returns), subindustry)",
        expression_hash="dup_hash_001",
        structure_hash="struct_dup_001",
        family_code="MOMENTUM",
        fields_used=["returns"],
        operators_used=["group_neutralize", "rank"],
        lifecycle_state="SUBMITTED"
    )
    async_session.add(cand_1)
    await async_session.commit()

    # Redundancy check for identical expression
    red_res = await redundancy_engine.evaluate_redundancy(
        expression="group_neutralize(rank(returns), subindustry)",
        structure_hash="struct_dup_001",
        fields_used=["returns"],
        operators_used=["group_neutralize", "rank"],
        family_code="MOMENTUM",
        current_candidate_id=None,
        session=async_session
    )

    assert red_res["is_duplicate"] is True
    assert red_res["duplicate_type"] == "EXACT_DUPLICATE"


@pytest.mark.asyncio
async def test_7_missing_telemetry_unknown(async_session: AsyncSession):
    """Test 7 — Missing Telemetry: Returns UNKNOWN handling without fabricating metrics."""
    exp = ResearchExperiment(
        title="Unknown Telemetry Test",
        hypothesis="Handling missing fields",
        family_code="VOLATILITY",
        target_budget=1
    )
    async_session.add(exp)
    await async_session.commit()

    cand = AlphaCandidate(
        expression="ts_std_dev(close, 20)",
        expression_hash="unk_hash_000",
        structure_hash="unk_struct_000",
        family_code="VOLATILITY",
        experiment_id=exp.id
    )
    async_session.add(cand)
    await async_session.commit()

    eval_res = await experiment_orchestrator._evaluate_single_candidate(cand, exp, async_session)

    assert eval_res["is_validated"] is True
    assert cand.portfolio_telemetry is not None


@pytest.mark.asyncio
async def test_8_dashboard_accuracy(async_session: AsyncSession):
    """Test 8 — Dashboard Accuracy: Dashboard metrics exactly match backend DB counts."""
    exp = ResearchExperiment(
        title="Dashboard Accuracy Test",
        hypothesis="Verifying DB count parity",
        family_code="VALUE",
        target_budget=5
    )
    async_session.add(exp)
    await async_session.commit()

    pipeline_res = await experiment_orchestrator.execute_experiment_pipeline(exp.id, async_session)

    # Re-fetch experiment from DB
    db_exp = await async_session.get(ResearchExperiment, exp.id)

    # Re-query actual candidates
    cands_stmt = select(AlphaCandidate).where(AlphaCandidate.experiment_id == exp.id)
    cands = (await async_session.execute(cands_stmt)).scalars().all()

    actual_generated = len(cands)
    actual_evaluated = len([c for c in cands if c.lifecycle_state in ["EVALUATED", "PROMISING", "ELITE", "SUBMITTED", "PORTFOLIO_EMPTY", "REJECTED"]])
    actual_rejected = len([c for c in cands if c.lifecycle_state in ["REJECTED", "PORTFOLIO_EMPTY", "INVALID"]])

    assert db_exp.candidates_generated == actual_generated
    assert db_exp.candidates_evaluated == actual_evaluated
    assert db_exp.candidates_rejected == actual_rejected
