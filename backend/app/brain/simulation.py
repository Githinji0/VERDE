import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.brain.client import brain_client
from backend.app.brain.response_parser import response_parser
from backend.app.core.logging import verde_logger
from backend.app.core.security import vault
from backend.app.database.models import AlphaCandidate, BrainConnection, BrainSession, ResearchScore, Simulation, SimulationMetric
from backend.app.database.session import AsyncSessionFactory
from backend.app.research.memory import research_memory
from backend.app.research.pareto import pareto_engine
from backend.app.research.scoring import alpha_scorer


class SimulationOrchestrator:
    """Manages the full lifecycle of simulations from submission through state-machine transitions, background polling, and metric extraction."""

    async def execute_simulation(
        self,
        candidate_id: str,
        session: AsyncSession,
        settings_dict: Optional[Dict[str, Any]] = None
    ) -> Simulation:
        """Submits a candidate expression to BRAIN and tracks state transitions."""
        # 1. Fetch Candidate
        candidate_stmt = select(AlphaCandidate).where(AlphaCandidate.id == candidate_id)
        candidate_res = await session.execute(candidate_stmt)
        candidate = candidate_res.scalar_one_or_none()

        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found.")

        # 2. Fetch Active BRAIN Connection
        conn_stmt = select(BrainConnection).where(BrainConnection.status == "CONNECTED", BrainConnection.is_active == True)
        conn_res = await session.execute(conn_stmt)
        brain_conn = conn_res.scalars().first()

        cookies = None
        environment = brain_conn.environment if brain_conn else "SIMULATION"

        if brain_conn:
            # Check for active session cookie
            sess_stmt = select(BrainSession).where(BrainSession.connection_id == brain_conn.id, BrainSession.is_valid == True)
            sess_res = await session.execute(sess_stmt)
            brain_sess = sess_res.scalars().first()
            if brain_sess and brain_sess.encrypted_session_cookie:
                try:
                    cookie_str = vault.decrypt(brain_sess.encrypted_session_cookie)
                    cookies = json.loads(cookie_str)
                except Exception:
                    pass

        # 3. Create Simulation Record in DB
        sim_settings = settings_dict or {
            "instrumentType": "EQUITY",
            "universe": "TOP3000",
            "region": "USA",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "language": "FASTEXPR"
        }

        simulation = Simulation(
            candidate_id=candidate.id,
            status="SUBMITTING",
            classification="PENDING",
            universe=sim_settings.get("universe", "TOP3000"),
            region=sim_settings.get("region", "USA"),
            delay=sim_settings.get("delay", 1),
            decay=sim_settings.get("decay", 0),
            neutralization=sim_settings.get("neutralization", "SUBINDUSTRY"),
            truncation=sim_settings.get("truncation", 0.08),
            pasteurization=sim_settings.get("pasteurization", "ON"),
            language=sim_settings.get("language", "FASTEXPR"),
            submitted_at=datetime.now(timezone.utc)
        )
        session.add(simulation)
        await session.commit()
        await session.refresh(simulation)

        # 4. Submit via Brain Client
        submission_result = await brain_client.submit_simulation(
            expression=candidate.expression,
            settings_dict=sim_settings,
            cookies=cookies,
            environment=environment,
            family_code=candidate.family_code or "MOMENTUM"
        )

        if submission_result["status"] == "COMPLETE":
            simulation.brain_sim_id = submission_result.get("brain_sim_id")
            await self.update_simulation_from_response(
                simulation,
                submission_result.get("data") or submission_result.get("raw_response") or {},
                session
            )
        elif submission_result["status"] == "SUBMITTED":
            simulation.brain_sim_id = submission_result.get("brain_sim_id")
            simulation.status = "RUNNING"
            await session.commit()
            verde_logger.log_event(
                event="SIMULATION_RUNNING",
                component="SIMULATION_ENGINE",
                candidate_id=candidate.id,
                simulation_id=simulation.id,
                message=f"Simulation running with BRAIN ID: {simulation.brain_sim_id}"
            )
            # Launch background polling task to automatically resolve simulation to completion
            asyncio.create_task(self._poll_simulation_background(simulation.id, simulation.brain_sim_id, cookies))
        else:
            status_code = submission_result.get("status_code", 500)
            parsed = response_parser.parse_simulation_response(
                data=submission_result.get("raw_response") or {"error": submission_result.get("error_message")},
                expression=candidate.expression,
                settings_dict=sim_settings,
                http_status=status_code,
                simulation_id=simulation.id
            )
            simulation.status = parsed["classification"]
            simulation.classification = parsed["classification"]
            simulation.portfolio_status = parsed.get("portfolio_status", "UNKNOWN")
            simulation.metrics_status = parsed.get("metrics_status", "UNAVAILABLE")
            simulation.remote_status = parsed.get("remote_status", "ERROR")
            simulation.diagnostic_code = parsed.get("diagnostic_code", "NONE")
            simulation.root_cause_type = parsed.get("root_cause", {}).get("type")
            simulation.root_cause_confidence = parsed.get("root_cause", {}).get("confidence", "UNKNOWN")
            simulation.diagnostic_details = {
                "root_cause": parsed.get("root_cause"),
                "evidence": parsed.get("evidence"),
                "component_tests": parsed.get("component_tests"),
                "signal_stats": parsed.get("signal_stats"),
                "configuration": parsed.get("configuration")
            }
            simulation.diagnostic_reason = parsed["diagnostic_reason"]
            simulation.possible_cause = parsed["possible_cause"]
            simulation.raw_response = submission_result.get("raw_response")
            await session.commit()

        return simulation

    async def reconcile_running_simulations(self, session: AsyncSession, max_age_seconds: int = 180) -> int:
        """
        Sweeps and reconciles all simulations stuck in RUNNING or SUBMITTING state.
        Executes sandbox evaluation for sbx_ IDs or offline modes, polls BRAIN for live IDs,
        and marks aged-out simulations as TIMEOUT / REMOTE_FAILURE.
        """
        stmt = select(Simulation).where(
            Simulation.status.in_(["RUNNING", "SUBMITTING"])
        )
        res = await session.execute(stmt)
        running_sims = res.scalars().all()

        if not running_sims:
            return 0

        # Fetch active cookies if any
        cookies = None
        conn_stmt = select(BrainConnection).where(BrainConnection.status == "CONNECTED", BrainConnection.is_active == True)
        conn_res = await session.execute(conn_stmt)
        brain_conn = conn_res.scalars().first()
        if brain_conn:
            sess_stmt = select(BrainSession).where(BrainSession.connection_id == brain_conn.id, BrainSession.is_valid == True)
            sess_res = await session.execute(sess_stmt)
            brain_sess = sess_res.scalars().first()
            if brain_sess and brain_sess.encrypted_session_cookie:
                try:
                    cookie_str = vault.decrypt(brain_sess.encrypted_session_cookie)
                    cookies = json.loads(cookie_str)
                except Exception:
                    pass

        now = datetime.now(timezone.utc)
        reconciled_count = 0

        for sim in running_sims:
            sub_time = sim.submitted_at
            if sub_time and sub_time.tzinfo is None:
                sub_time = sub_time.replace(tzinfo=timezone.utc)
            age_secs = (now - sub_time).total_seconds() if sub_time else 9999

            # Case A: Sandbox simulation (starts with sbx_ or no brain_sim_id or brain_conn is null/SIMULATION)
            if not sim.brain_sim_id or sim.brain_sim_id.startswith("sbx_") or not brain_conn or brain_conn.environment == "SIMULATION":
                from backend.app.brain.simulator import simulation_sandbox
                cand_stmt = select(AlphaCandidate).where(AlphaCandidate.id == sim.candidate_id)
                cand_res = await session.execute(cand_stmt)
                candidate = cand_res.scalar_one_or_none()
                expr = candidate.expression if candidate else "returns"
                family = candidate.family_code if candidate else "MOMENTUM"
                
                settings_dict = {
                    "universe": sim.universe or "TOP3000",
                    "region": sim.region or "USA",
                    "delay": sim.delay if sim.delay is not None else 1,
                    "decay": sim.decay if sim.decay is not None else 0,
                    "neutralization": sim.neutralization or "SUBINDUSTRY"
                }
                sbx_data = simulation_sandbox.simulate(expr, settings_dict, family_code=family)
                if not sim.brain_sim_id:
                    import hashlib
                    sim.brain_sim_id = f"sbx_{hashlib.sha256(expr.encode()).hexdigest()[:10]}"

                await self.update_simulation_from_response(sim, sbx_data, session, http_status=200)
                reconciled_count += 1
                continue

            # Case B: Aged-out simulation (stuck longer than max_age_seconds)
            if age_secs > max_age_seconds:
                timeout_data = {
                    "error": f"Simulation timed out after {int(age_secs)}s without resolution from BRAIN cluster.",
                    "message": "Remote simulation timeout."
                }
                await self.update_simulation_from_response(sim, timeout_data, session, http_status=408)
                reconciled_count += 1
                continue

            # Case C: Live BRAIN simulation polling
            try:
                poll_res = await brain_client.poll_simulation_status(sim.brain_sim_id, cookies=cookies)
                status_code = poll_res.get("status_code", 200)
                data = poll_res.get("data", {})
                
                if status_code in (200, 400, 401, 403, 404, 429, 500):
                    status_str = data.get("status", "").upper() if isinstance(data, dict) else ""
                    is_complete = status_str in ("COMPLETE", "ERROR", "CANCELLED") or "records" in data or "stats" in data or status_code != 200
                    
                    if is_complete:
                        payload_data = data if isinstance(data, dict) and data else {"error": poll_res.get("error_message") or f"Poll returned HTTP {status_code}"}
                        await self.update_simulation_from_response(sim, payload_data, session, http_status=status_code)
                        reconciled_count += 1
            except Exception as e:
                verde_logger.log_event(
                    event="RECONCILE_SIM_ERROR",
                    severity="WARNING",
                    component="SIMULATION_ENGINE",
                    message=f"Error reconciling simulation {sim.id}: {str(e)}"
                )

        return reconciled_count

    async def _poll_simulation_background(self, simulation_id: str, brain_sim_id: str, cookies: Optional[Dict[str, str]] = None):
        """Asynchronously polls BRAIN simulation until complete and triggers result processing."""
        is_sandbox = not brain_sim_id or brain_sim_id.startswith("sbx_")
        
        for attempt in range(1, 150):
            await asyncio.sleep(2.0 if not is_sandbox else 0.5)
            try:
                async with AsyncSessionFactory() as session:
                    sim_stmt = select(Simulation).where(Simulation.id == simulation_id)
                    res = await session.execute(sim_stmt)
                    sim = res.scalar_one_or_none()
                    if not sim or sim.status not in ("RUNNING", "SUBMITTING"):
                        break

                    if is_sandbox:
                        await self.reconcile_running_simulations(session)
                        break

                    poll_res = await brain_client.poll_simulation_status(brain_sim_id, cookies=cookies)
                    status_code = poll_res.get("status_code", 200)
                    data = poll_res.get("data", {})
                    status = data.get("status", "").upper() if isinstance(data, dict) else ""

                    if status in ("COMPLETE", "ERROR", "CANCELLED") or "records" in data or "stats" in data or status_code != 200:
                        payload_data = data if isinstance(data, dict) and data else {"error": poll_res.get("error_message") or f"Poll returned HTTP {status_code}"}
                        await self.update_simulation_from_response(
                            sim,
                            payload_data,
                            session,
                            http_status=status_code
                        )
                        break
            except Exception as e:
                verde_logger.log_event(
                    event="POLL_BACKGROUND_ERROR",
                    severity="WARNING",
                    component="SIMULATION_ENGINE",
                    message=f"Error in background simulation polling ({simulation_id}): {str(e)}"
                )

    async def update_simulation_from_response(
        self,
        simulation: Simulation,
        raw_response_data: Dict[str, Any],
        session: AsyncSession,
        http_status: int = 200
    ) -> Simulation:
        """Parses BRAIN response and updates simulation records, candidate tiers, memory, and Pareto rankings."""
        cand_stmt = select(AlphaCandidate).where(AlphaCandidate.id == simulation.candidate_id)
        c_res = await session.execute(cand_stmt)
        candidate = c_res.scalar_one_or_none()

        sim_settings = {
            "universe": simulation.universe or "TOP3000",
            "region": simulation.region or "USA",
            "delay": simulation.delay if simulation.delay is not None else 1,
            "decay": simulation.decay if simulation.decay is not None else 0,
            "neutralization": simulation.neutralization or "SUBINDUSTRY",
            "truncation": simulation.truncation if simulation.truncation is not None else 0.08,
            "pasteurization": simulation.pasteurization or "ON",
            "language": simulation.language or "FASTEXPR"
        }

        expr = candidate.expression if candidate else ""
        parsed = response_parser.parse_simulation_response(
            data=raw_response_data,
            expression=expr,
            settings_dict=sim_settings,
            http_status=http_status,
            simulation_id=simulation.id,
            brain_sim_id=simulation.brain_sim_id
        )

        simulation.raw_response = raw_response_data
        simulation.classification = parsed["classification"]
        simulation.portfolio_status = parsed["portfolio_status"]
        simulation.metrics_status = parsed["metrics_status"]
        simulation.remote_status = parsed.get("remote_status")
        simulation.diagnostic_code = parsed.get("diagnostic_code", "NONE")
        simulation.root_cause_type = parsed.get("root_cause", {}).get("type")
        simulation.root_cause_confidence = parsed.get("root_cause", {}).get("confidence", "UNKNOWN")
        simulation.position_count = parsed.get("position_count")
        simulation.diagnostic_details = {
            "root_cause": parsed.get("root_cause"),
            "evidence": parsed.get("evidence"),
            "component_tests": parsed.get("component_tests"),
            "signal_stats": parsed.get("signal_stats"),
            "configuration": parsed.get("configuration")
        }
        simulation.diagnostic_reason = parsed["diagnostic_reason"]
        simulation.possible_cause = parsed["possible_cause"]
        simulation.completed_at = datetime.now(timezone.utc)

        if parsed["classification"] == "PORTFOLIO_EMPTY":
            simulation.status = "PORTFOLIO_EMPTY"
        elif parsed["classification"] == "VALID_METRICS":
            simulation.status = "METRICS_AVAILABLE"
        elif parsed["classification"] == "ALPHA_FAILURE":
            simulation.status = "ALPHA_FAILURE"
        elif parsed["classification"] == "AUTH_FAILURE":
            simulation.status = "AUTH_FAILURE"
        elif parsed["classification"] == "REMOTE_FAILURE":
            simulation.status = "REMOTE_FAILURE"
        elif parsed["classification"] == "TECHNICAL_FAILURE":
            simulation.status = "TECHNICAL_FAILURE"
        else:
            simulation.status = parsed.get("remote_status") or "COMPLETE"

        # Create or update metrics record
        metric_stmt = select(SimulationMetric).where(SimulationMetric.simulation_id == simulation.id)
        m_res = await session.execute(metric_stmt)
        metric = m_res.scalar_one_or_none()

        if not metric:
            metric = SimulationMetric(
                simulation_id=simulation.id,
                sharpe=parsed["sharpe"],
                fitness=parsed["fitness"],
                turnover=parsed["turnover"],
                margin_bps=parsed["margin_bps"],
                returns_annualized=parsed["returns_annualized"],
                drawdown_max=parsed["drawdown_max"],
                long_count=parsed["long_count"],
                short_count=parsed["short_count"],
                has_valid_metrics=parsed["has_valid_metrics"]
            )
            session.add(metric)
        else:
            metric.sharpe = parsed["sharpe"]
            metric.fitness = parsed["fitness"]
            metric.turnover = parsed["turnover"]
            metric.margin_bps = parsed["margin_bps"]
            metric.returns_annualized = parsed["returns_annualized"]
            metric.drawdown_max = parsed["drawdown_max"]
            metric.long_count = parsed["long_count"]
            metric.short_count = parsed["short_count"]
            metric.has_valid_metrics = parsed["has_valid_metrics"]

        await session.flush()

        # Update candidate state, tier, and research score
        cand_stmt = select(AlphaCandidate).where(AlphaCandidate.id == simulation.candidate_id)
        c_res = await session.execute(cand_stmt)
        candidate = c_res.scalar_one_or_none()

        if candidate:
            # Calculate Research Score
            score_data = alpha_scorer.calculate_research_score(
                sharpe=parsed["sharpe"],
                fitness=parsed["fitness"],
                turnover=parsed["turnover"],
                margin_bps=parsed["margin_bps"],
                complexity=candidate.complexity_score or 1.0
            )

            if score_data:
                sc_stmt = select(ResearchScore).where(ResearchScore.candidate_id == candidate.id)
                sc_res = await session.execute(sc_stmt)
                r_score = sc_res.scalar_one_or_none()

                if not r_score:
                    r_score = ResearchScore(candidate_id=candidate.id)
                    session.add(r_score)

                r_score.total_score = score_data["total_score"]
                r_score.sharpe_component = score_data["sharpe_component"]
                r_score.fitness_component = score_data["fitness_component"]
                r_score.turnover_component = score_data["turnover_component"]
                r_score.stability_component = score_data["stability_component"]
                r_score.robustness_component = score_data["robustness_component"]
                r_score.diversity_component = score_data["diversity_component"]
                r_score.simplicity_component = score_data["simplicity_component"]
                r_score.complexity_penalty = score_data["complexity_penalty"]
                r_score.is_target_passing = score_data["is_target_passing"]
                r_score.is_candidate_ready = score_data["is_candidate_ready"]

                if score_data["is_target_passing"]:
                    candidate.tier = "TIER_4_TARGET_PASSING"
                elif score_data["is_candidate_ready"]:
                    candidate.tier = "TIER_3_NEAR_MISS"
                else:
                    candidate.tier = "TIER_2_PREFLIGHT_PASSED"

            # Update empirical research memory
            try:
                await research_memory.update_memory_from_simulation(session, candidate, simulation, metric)
            except Exception as mem_err:
                verde_logger.log_event(
                    event="MEMORY_UPDATE_WARN",
                    severity="WARNING",
                    component="RESEARCH_MEMORY",
                    message=f"Memory update notice: {str(mem_err)}"
                )

        # Update Pareto rankings across all valid candidates
        try:
            await pareto_engine.update_pareto_front_db(session)
        except Exception as pareto_err:
            verde_logger.log_event(
                event="PARETO_UPDATE_WARN",
                severity="WARNING",
                component="PARETO_ENGINE",
                message=f"Pareto frontier update notice: {str(pareto_err)}"
            )

        await session.commit()
        await session.refresh(simulation)

        verde_logger.log_event(
            event=f"SIMULATION_{simulation.status}",
            severity="INFO" if parsed["has_valid_metrics"] else "WARNING",
            component="SIMULATION_ENGINE",
            candidate_id=simulation.candidate_id,
            simulation_id=simulation.id,
            message=f"Simulation result: {simulation.status} (Classification: {simulation.classification})",
            metadata={"sharpe": parsed["sharpe"], "fitness": parsed["fitness"], "turnover": parsed["turnover"]}
        )

        return simulation


simulation_orchestrator = SimulationOrchestrator()
