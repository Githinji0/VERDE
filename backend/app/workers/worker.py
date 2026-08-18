import asyncio
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from backend.app.brain.simulation import simulation_orchestrator
from backend.app.core.logging import verde_logger
from backend.app.database.models import AlphaCandidate, Simulation, SimulationMetric, WorkerJob
from backend.app.database.session import AsyncSessionFactory
from backend.app.generation.hypothesis_engine import hypothesis_engine
from backend.app.research.memory import research_memory
from backend.app.research.pareto import pareto_engine
from backend.app.research.scoring import alpha_scorer
from backend.app.workers.queue import job_queue


class ResearchWorker:
    """Async background worker executing queued generation, preflight, and simulation jobs."""

    def __init__(self):
        self._is_running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the worker processing loop."""
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._process_loop())
        verde_logger.log_event(
            event="WORKER_STARTED",
            component="RESEARCH_WORKER",
            message="Background research worker started."
        )

    async def stop(self):
        """Gracefully halts worker loop."""
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        verde_logger.log_event(
            event="WORKER_STOPPED",
            component="RESEARCH_WORKER",
            message="Background research worker halted."
        )

    async def _process_loop(self):
        last_sweep = 0.0
        while self._is_running:
            try:
                # Periodic simulation reconciliation sweep
                now_t = asyncio.get_event_loop().time()
                if now_t - last_sweep > 5.0:
                    last_sweep = now_t
                    try:
                        async with AsyncSessionFactory() as session:
                            await simulation_orchestrator.reconcile_running_simulations(session)
                    except Exception:
                        pass

                # Wait for next job with timeout to check running flag
                try:
                    priority, job_id, job_type, payload = await asyncio.wait_for(job_queue.dequeue_job(), timeout=2.0)
                except asyncio.TimeoutError:
                    continue

                await self._execute_job(job_id, job_type, payload)

            except asyncio.CancelledError:
                break
            except Exception as e:
                verde_logger.log_event(
                    event="WORKER_LOOP_ERROR",
                    severity="ERROR",
                    component="RESEARCH_WORKER",
                    message=f"Error in worker processing loop: {str(e)}"
                )
                await asyncio.sleep(1.0)

    async def _execute_job(self, job_id: str, job_type: str, payload: dict):
        async with AsyncSessionFactory() as session:
            try:
                # Update job status to RUNNING
                job_stmt = select(WorkerJob).where(WorkerJob.id == job_id)
                res = await session.execute(job_stmt)
                job = res.scalar_one_or_none()
                if job:
                    job.status = "RUNNING"
                    job.started_at = datetime.now(timezone.utc)
                    await session.commit()

                if job_type == "GENERATION":
                    family_code = payload.get("family_code", "MOMENTUM")
                    count = payload.get("count", 5)
                    await hypothesis_engine.generate_and_preflight_candidates(
                        family_code=family_code,
                        count=count,
                        session=session
                    )

                elif job_type == "SIMULATION":
                    candidate_id = payload.get("candidate_id")
                    settings_dict = payload.get("settings")
                    if candidate_id:
                        await simulation_orchestrator.execute_simulation(
                            candidate_id=candidate_id,
                            session=session,
                            settings_dict=settings_dict
                        )

                elif job_type == "EVOLUTION":
                    parent_expr = payload.get("parent_expression")
                    family_code = payload.get("family_code", "MOMENTUM")
                    from backend.app.research.evolution import evolution_engine
                    if parent_expr:
                        offspring = evolution_engine.mutate_candidate(parent_expr, family_code)
                        # Preflight & persist offspring candidate
                        await hypothesis_engine.generate_and_preflight_candidates(
                            family_code=family_code,
                            count=1,
                            session=session
                        )

                if job:
                    job.status = "COMPLETED"
                    job.completed_at = datetime.now(timezone.utc)
                    await session.commit()

            except Exception as e:
                verde_logger.log_event(
                    event="JOB_FAILED",
                    severity="ERROR",
                    component="RESEARCH_WORKER",
                    message=f"Job {job_id} ({job_type}) failed: {str(e)}"
                )
                if job:
                    job.status = "FAILED"
                    job.error_message = str(e)
                    job.completed_at = datetime.now(timezone.utc)
                    await session.commit()


research_worker = ResearchWorker()
