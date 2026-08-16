import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.brain.client import brain_client
from backend.app.brain.response_parser import response_parser
from backend.app.core.logging import verde_logger
from backend.app.core.security import vault
from backend.app.database.models import AlphaCandidate, BrainConnection, BrainSession, Simulation, SimulationMetric


class SimulationOrchestrator:
    """Manages the full lifecycle of simulations from submission through state-machine transitions and metric extraction."""

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
        if brain_conn:
            # Check for active session cookie
            sess_stmt = select(BrainSession).where(BrainSession.connection_id == brain_conn.id, BrainSession.is_valid == True)
            sess_res = await session.execute(sess_stmt)
            brain_sess = sess_res.scalars().first()
            if brain_sess and brain_sess.encrypted_session_cookie:
                try:
                    import json
                    cookie_str = vault.decrypt(brain_sess.encrypted_session_cookie)
                    cookies = json.loads(cookie_str)
                except Exception:
                    pass

        # 3. Create Simulation Record in DB
        sim_settings = settings_dict or {
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
            cookies=cookies
        )

        if submission_result["status"] in ("SUBMITTED", "COMPLETE"):
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
        else:
            simulation.status = submission_result.get("status", "SUBMISSION_ERROR")
            simulation.classification = "TECHNICAL_FAILURE"
            simulation.diagnostic_reason = submission_result.get("error_message")
            simulation.raw_response = submission_result.get("raw_response")
            await session.commit()

        return simulation

    async def update_simulation_from_response(
        self,
        simulation: Simulation,
        raw_response_data: Dict[str, Any],
        session: AsyncSession
    ) -> Simulation:
        """Parses BRAIN response and updates simulation records and metrics."""
        parsed = response_parser.parse_simulation_response(raw_response_data)
        
        simulation.raw_response = raw_response_data
        simulation.classification = parsed["classification"]
        simulation.portfolio_status = parsed["portfolio_status"]
        simulation.metrics_status = parsed["metrics_status"]
        simulation.diagnostic_reason = parsed["diagnostic_reason"]
        simulation.possible_cause = parsed["possible_cause"]
        simulation.completed_at = datetime.now(timezone.utc)
        
        if parsed["portfolio_status"] == "EMPTY":
            simulation.status = "PORTFOLIO_EMPTY"
        elif parsed["metrics_status"] == "AVAILABLE":
            simulation.status = "METRICS_AVAILABLE"
        elif parsed["metrics_status"] == "MISSING":
            simulation.status = "METRICS_MISSING"
        elif parsed["classification"] == "TECHNICAL_FAILURE":
            simulation.status = "TECHNICAL_FAILURE"
        else:
            simulation.status = "COMPLETE"

        # Create or update metrics record
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
