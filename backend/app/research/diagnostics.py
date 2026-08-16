import hashlib
import json
import re
from typing import Any, Dict, List, Optional
from backend.app.core.logging import verde_logger
from backend.app.generation.field_registry import FIELD_REGISTRY
from backend.app.generation.operator_registry import OPERATOR_REGISTRY


class SimulationDiagnosticEngine:
    """
    Comprehensive, evidence-based diagnostic engine for WorldQuant BRAIN alpha simulations.
    Distinguishes REMOTE_FAILURE, AUTH_FAILURE, ALPHA_FAILURE, PORTFOLIO_EMPTY,
    and METRICS_UNAVAILABLE. Categorizes evidence into OBSERVED, PROVEN, INFERRED,
    POSSIBLE, and UNKNOWN levels. Strictly avoids overclaiming high confidence
    without intermediate stage telemetry.
    """

    @classmethod
    def diagnose_simulation(
        cls,
        raw_response: Any,
        expression: str,
        settings_dict: Optional[Dict[str, Any]] = None,
        http_status: int = 200,
        simulation_id: Optional[str] = None,
        brain_sim_id: Optional[str] = None
    ) -> Dict[str, Any]:
        settings_dict = settings_dict or {}
        universe = settings_dict.get("universe", "TOP3000")
        region = settings_dict.get("region", "USA")
        delay = settings_dict.get("delay", 1)
        neutralization = settings_dict.get("neutralization", "SUBINDUSTRY")

        data = raw_response if isinstance(raw_response, dict) else {}
        
        # Categorized evidence containers
        observed: List[str] = []
        proven: List[str] = []
        inferred: List[str] = []
        possible: List[str] = []
        unknown: List[str] = []

        # 1. HTTP & Network Error Diagnosis
        if http_status in (401, 403):
            observed.append(f"HTTP status {http_status} received from BRAIN authentication endpoint.")
            proven.append("BRAIN rejected credentials or session token expired.")
            return cls._build_diagnostic(
                classification="AUTH_FAILURE",
                remote_status="UNAUTHORIZED",
                portfolio_state="UNKNOWN",
                metrics_state="UNAVAILABLE",
                diagnostic_code="AUTH_FAILED",
                root_cause_type="AUTHENTICATION_FAILURE",
                confidence="HIGH",
                root_cause_message="WorldQuant BRAIN rejected credentials or session token expired.",
                observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
                simulation_id=simulation_id, brain_sim_id=brain_sim_id,
                expression=expression, settings_dict=settings_dict, http_status=http_status
            )

        if http_status == 429:
            observed.append("HTTP status 429 received from simulation endpoint.")
            proven.append("WorldQuant BRAIN rate limit reached on simulation cluster.")
            return cls._build_diagnostic(
                classification="REMOTE_FAILURE",
                remote_status="RATE_LIMITED",
                portfolio_state="UNKNOWN",
                metrics_state="UNAVAILABLE",
                diagnostic_code="RATE_LIMITED",
                root_cause_type="RATE_LIMIT_EXCEEDED",
                confidence="HIGH",
                root_cause_message="WorldQuant BRAIN rate limit reached on simulation cluster.",
                observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
                simulation_id=simulation_id, brain_sim_id=brain_sim_id,
                expression=expression, settings_dict=settings_dict, http_status=http_status
            )

        if http_status >= 500 or "timeout" in str(data).lower():
            observed.append(f"Remote server error response with HTTP {http_status}.")
            proven.append(f"WorldQuant BRAIN cluster returned server error {http_status}.")
            return cls._build_diagnostic(
                classification="REMOTE_FAILURE",
                remote_status="SERVER_ERROR",
                portfolio_state="UNKNOWN",
                metrics_state="UNAVAILABLE",
                diagnostic_code="SERVER_ERROR",
                root_cause_type="REMOTE_SERVER_FAILURE",
                confidence="HIGH",
                root_cause_message=f"WorldQuant BRAIN cluster returned HTTP {http_status} server error.",
                observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
                simulation_id=simulation_id, brain_sim_id=brain_sim_id,
                expression=expression, settings_dict=settings_dict, http_status=http_status
            )

        # 2. Remote Syntax / Compilation Error Check
        remote_error = data.get("error") or data.get("message")
        if remote_error and not data.get("records") and not data.get("stats"):
            err_str = str(remote_error)
            observed.append(f"Remote engine returned error: {err_str}")
            proven.append(f"BRAIN engine explicitly rejected expression: {err_str}")
            return cls._build_diagnostic(
                classification="ALPHA_FAILURE",
                remote_status="ERROR",
                portfolio_state="EMPTY",
                metrics_state="UNAVAILABLE",
                diagnostic_code="COMPILATION_ERROR",
                root_cause_type="SYNTAX_OR_FIELD_ERROR",
                confidence="HIGH",
                root_cause_message=f"BRAIN failed to compile or evaluate alpha expression: {err_str}",
                observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
                simulation_id=simulation_id, brain_sim_id=brain_sim_id,
                expression=expression, settings_dict=settings_dict, http_status=http_status
            )

        # 3. Inspect Portfolio Positions and Metrics
        stats = data.get("stats") or data.get("summary") or {}
        records = data.get("records") or data.get("pnl") or []

        def parse_float(val: Any) -> Optional[float]:
            if val is None or val == "" or val == "N/A" or val == "null":
                return None
            try:
                f = float(val)
                return None if f != f else f
            except (ValueError, TypeError):
                return None

        sharpe = parse_float(stats.get("sharpe") or data.get("sharpe"))
        fitness = parse_float(stats.get("fitness") or data.get("fitness"))
        turnover = parse_float(stats.get("turnover") or data.get("turnover"))
        margin_bps = parse_float(stats.get("margin") or data.get("margin_bps") or stats.get("margin_bps"))
        returns = parse_float(stats.get("returns") or data.get("returns"))
        drawdown = parse_float(stats.get("drawdown") or stats.get("max_drawdown") or data.get("drawdown"))

        long_count = stats.get("longCount") if stats.get("longCount") is not None else data.get("longCount")
        short_count = stats.get("shortCount") if stats.get("shortCount") is not None else data.get("shortCount")

        if long_count is not None:
            try: long_count = int(long_count)
            except: pass
        if short_count is not None:
            try: short_count = int(short_count)
            except: pass

        position_count = (long_count or 0) + (short_count or 0)
        has_positions = position_count > 0 or (isinstance(records, list) and len(records) > 0 and sharpe is not None)

        # 4. Success Case (Valid Portfolio with Metrics)
        if has_positions and sharpe is not None and fitness is not None:
            observed.append(f"Simulation completed with {position_count} active positions ({long_count or 0} long, {short_count or 0} short).")
            observed.append(f"Performance metrics extracted: Sharpe={sharpe}, Fitness={fitness}, Turnover={turnover}.")
            proven.append("Simulation completed successfully with active positions and valid statistical metrics.")
            return cls._build_diagnostic(
                classification="VALID_METRICS",
                remote_status="COMPLETE",
                portfolio_state="VALID",
                metrics_state="AVAILABLE",
                diagnostic_code="VALID_ALPHA",
                root_cause_type="NONE",
                confidence="HIGH",
                root_cause_message="Simulation completed successfully with active positions and valid statistical metrics.",
                observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
                position_count=position_count, long_count=long_count, short_count=short_count,
                sharpe=sharpe, fitness=fitness, turnover=turnover, margin_bps=margin_bps,
                returns=returns, drawdown=drawdown,
                simulation_id=simulation_id, brain_sim_id=brain_sim_id,
                expression=expression, settings_dict=settings_dict, http_status=http_status
            )

        # 5. Deep Diagnostics for PORTFOLIO_EMPTY
        observed.append("Simulation completed remotely with 0 final positions.")
        observed.append("Metrics are classified as METRICS_UNAVAILABLE due to empty portfolio positions.")
        proven.append("Final portfolio position count is zero.")

        # Deconstruct and analyze expression components
        component_tests = cls._evaluate_subexpression_hierarchy(expression)
        signal_stats = cls._analyze_signal_characteristics(expression, data)

        # Build position pipeline tracking object
        position_pipeline = cls._build_position_pipeline(data, position_count=0)

        # Investigate specific structural causes
        has_group_neutralize = "group_neutralize" in expression.lower()
        has_subindustry_group = "subindustry" in expression.lower()
        is_subindustry_settings = str(neutralization).upper() == "SUBINDUSTRY"

        if has_group_neutralize:
            observed.append("Formula contains explicit group_neutralize().")
        if is_subindustry_settings:
            observed.append("Simulation configuration specifies neutralization='SUBINDUSTRY'.")

        # Unknown intermediate telemetry stages
        unknown.append("Intermediate post-ranking signal values across instruments")
        unknown.append("Post-expression neutralization weights")
        unknown.append("Post-simulation neutralization weights")
        unknown.append("Post-truncation weights")
        unknown.append("Tradeability-stage weights")

        root_cause_type = "UNVERIFIED_EMPTY_PORTFOLIO"
        root_cause_message = "Simulation completed on BRAIN cluster without generating any tradeable positions."
        confidence = "LOW"
        why_not_proven = (
            "The BRAIN simulation completed with 0 positions, but the returned API response does not "
            "expose intermediate weight matrices or pipeline stage counts. Complete collapse cannot be confirmed "
            "at a specific stage without intermediate telemetry."
        )

        # Check for proven measured zero intermediate weights (if telemetry provided in data)
        post_neut_weights = data.get("post_neutralization_weights")
        post_trunc_weights = data.get("post_truncation_weights")
        tradeable_weights = data.get("tradeable_weights")

        if post_neut_weights == 0:
            root_cause_type = "NEUTRALIZATION_COLLAPSE"
            confidence = "HIGH"
            why_not_proven = None
            proven.append("Post-neutralization weight count was measured at zero.")
            root_cause_message = "Group neutralization de-meaning reduced all active instrument weights to zero."
        elif post_trunc_weights == 0 and post_neut_weights and post_neut_weights > 0:
            root_cause_type = "TRUNCATION_COLLAPSE"
            confidence = "HIGH"
            why_not_proven = None
            proven.append("Post-truncation weight count collapsed to zero from non-zero neutralization weights.")
            root_cause_message = "Position truncation threshold eliminated all active weight allocations."
        elif tradeable_weights == 0 and post_trunc_weights and post_trunc_weights > 0:
            root_cause_type = "TRADEABILITY_COLLAPSE"
            confidence = "HIGH"
            why_not_proven = None
            proven.append("Tradeability liquidity filtering eliminated all non-zero position weights.")
            root_cause_message = "Liquidity or tradeability constraints removed all remaining position weights."
        elif signal_stats.get("is_constant") is True:
            root_cause_type = "CONSTANT_SIGNAL"
            confidence = "HIGH"
            why_not_proven = None
            proven.append(f"Signal evaluated to constant uniform value (unique_count={signal_stats.get('unique_count')}).")
            root_cause_message = "Signal values evaluated to uniform constant values across all eligible instruments."
        elif has_group_neutralize and has_subindustry_group and is_subindustry_settings:
            root_cause_type = "POTENTIAL_REDUNDANT_NEUTRALIZATION"
            confidence = "LOW"
            inferred.append("Redundant subindustry neutralization may contribute to cross-sectional signal collapse.")
            possible.append("Intra-subindustry rank de-meaning followed by simulation subindustry centering may fall below truncation thresholds.")
            root_cause_message = (
                "The alpha contains explicit SUBINDUSTRY neutralization while simulation settings also enforce "
                "SUBINDUSTRY neutralization. This is a possible contributor to signal reduction, but complete portfolio "
                "collapse at this stage has not been independently proven."
            )
            why_not_proven = (
                "The alpha contains explicit SUBINDUSTRY neutralization and the simulation also requests SUBINDUSTRY "
                "neutralization. This is a potential source of signal reduction, but the available BRAIN response does not "
                "expose intermediate weights, so complete portfolio collapse at this stage cannot be confirmed."
            )

        # Generate recommended control experiments for A/B testing
        recommended_experiments = cls._build_recommended_experiments(expression, neutralization)

        return cls._build_diagnostic(
            classification="PORTFOLIO_EMPTY",
            remote_status="PORTFOLIO_EMPTY",
            portfolio_state="EMPTY",
            metrics_state="UNAVAILABLE",
            diagnostic_code="PORTFOLIO_EMPTY",
            root_cause_type=root_cause_type,
            confidence=confidence,
            root_cause_message=root_cause_message,
            why_not_proven=why_not_proven,
            observed=observed, proven=proven, inferred=inferred, possible=possible, unknown=unknown,
            component_tests=component_tests,
            signal_stats=signal_stats,
            position_pipeline=position_pipeline,
            recommended_experiments=recommended_experiments,
            position_count=0, long_count=0, short_count=0,
            sharpe=None, fitness=None, turnover=turnover, margin_bps=margin_bps,
            returns=returns, drawdown=drawdown,
            simulation_id=simulation_id, brain_sim_id=brain_sim_id,
            expression=expression, settings_dict=settings_dict, http_status=http_status
        )

    @classmethod
    def _build_position_pipeline(cls, data: Dict[str, Any], position_count: int = 0) -> Dict[str, Any]:
        """Tracks position pipeline counts across stages if observable, otherwise marks NOT_OBSERVABLE."""
        pipeline = {
            "universe_count": data.get("universe_count") or 3000,
            "eligible_count": data.get("eligible_count") if data.get("eligible_count") is not None else "NOT_OBSERVABLE",
            "raw_signal_count": data.get("raw_signal_count") if data.get("raw_signal_count") is not None else "NOT_OBSERVABLE",
            "pre_neutralization_weights": data.get("pre_neutralization_weights") if data.get("pre_neutralization_weights") is not None else "NOT_OBSERVABLE",
            "post_neutralization_weights": data.get("post_neutralization_weights") if data.get("post_neutralization_weights") is not None else "NOT_OBSERVABLE",
            "post_truncation_weights": data.get("post_truncation_weights") if data.get("post_truncation_weights") is not None else "NOT_OBSERVABLE",
            "tradeable_instruments": data.get("tradeable_instruments") if data.get("tradeable_instruments") is not None else "NOT_OBSERVABLE",
            "final_positions": position_count
        }

        # Determine last nonzero stage
        stages_order = [
            ("universe_count", pipeline["universe_count"]),
            ("eligible_count", pipeline["eligible_count"]),
            ("raw_signal_count", pipeline["raw_signal_count"]),
            ("pre_neutralization_weights", pipeline["pre_neutralization_weights"]),
            ("post_neutralization_weights", pipeline["post_neutralization_weights"]),
            ("post_truncation_weights", pipeline["post_truncation_weights"]),
            ("tradeable_instruments", pipeline["tradeable_instruments"]),
            ("final_positions", pipeline["final_positions"])
        ]

        last_nonzero = "UNKNOWN (Intermediate telemetry not exposed by BRAIN API)"
        for name, val in stages_order:
            if isinstance(val, int) and val > 0:
                last_nonzero = f"{name} ({val})"

        pipeline["last_nonzero_stage"] = last_nonzero
        return pipeline

    @classmethod
    def _build_recommended_experiments(cls, expression: str, neutralization: str) -> List[Dict[str, Any]]:
        """Generates clean diagnostic A/B control experiment suggestions."""
        experiments = []
        clean_expr = expression.strip()

        if "group_neutralize(" in clean_expr:
            # Control A: Remove group_neutralize wrapper
            no_group_expr = re.sub(r'group_neutralize\((.*),\s*\w+\)', r'\1', clean_expr)
            experiments.append({
                "name": "Control A — Remove Explicit Group Neutralization",
                "expression": no_group_expr,
                "neutralization": neutralization,
                "notes": "Tests whether removing formula-level neutralization allows simulation-level neutralization to retain active positions."
            })

            # Control B: Set simulation neutralization to NONE
            experiments.append({
                "name": "Control B — Disable Simulation Neutralization",
                "expression": clean_expr,
                "neutralization": "NONE",
                "notes": "Tests whether disabling portfolio-level SUBINDUSTRY neutralization preserves active weights from formula-level group_neutralize."
            })
        else:
            experiments.append({
                "name": "Control A — Test Without Neutralization",
                "expression": clean_expr,
                "neutralization": "NONE",
                "notes": "Tests unconstrained raw signal position generation."
            })

        return experiments

    @classmethod
    def _evaluate_subexpression_hierarchy(cls, expression: str, portfolio_state: str = "EMPTY") -> List[Dict[str, Any]]:
        """Deconstructs complex formula into layered AST component hierarchy using canonical AST parser."""
        from backend.app.generation.ast_parser import ast_parser
        is_empty = (portfolio_state == "EMPTY")
        return ast_parser.extract_component_hierarchy(expression, is_empty_portfolio=is_empty)

    @classmethod
    def _analyze_signal_characteristics(cls, expression: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates mathematical signal properties. Reports NOT_OBSERVABLE if telemetry is missing."""
        clean = expression.strip().lower()

        if clean in ("1", "0"):
            return {
                "status": "OBSERVED",
                "min": 1.0 if clean == "1" else 0.0,
                "max": 1.0 if clean == "1" else 0.0,
                "mean": 1.0 if clean == "1" else 0.0,
                "std": 0.0,
                "unique_count": 1,
                "is_constant": True,
                "all_null": False
            }

        # Check if actual signal statistics are present in response telemetry
        sig_data = data.get("signal_stats") or data.get("signal_summary")
        if isinstance(sig_data, dict):
            unique_cnt = sig_data.get("unique_count")
            std_val = sig_data.get("std")
            is_const = (unique_cnt is not None and unique_cnt <= 1) or (std_val is not None and std_val == 0)
            return {
                "status": "OBSERVED",
                "min": sig_data.get("min"),
                "max": sig_data.get("max"),
                "mean": sig_data.get("mean"),
                "std": std_val,
                "unique_count": unique_cnt,
                "null_count": sig_data.get("null_count", 0),
                "nan_count": sig_data.get("nan_count", 0),
                "is_constant": is_const,
                "all_null": bool(sig_data.get("all_null"))
            }

        return {
            "status": "NOT_OBSERVABLE",
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "unique_count": None,
            "null_count": None,
            "nan_count": None,
            "is_constant": "UNKNOWN",
            "all_null": "UNKNOWN",
            "notes": "Signal statistics unavailable locally without intermediate array telemetry."
        }

    @staticmethod
    def sanitize_telemetry(data: Any) -> Any:
        """Redacts credentials, cookies, and secret tokens from raw response telemetry."""
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(sec in str(k).lower() for sec in ["password", "token", "cookie", "secret", "authorization", "csrf", "bearer"]):
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = SimulationDiagnosticEngine.sanitize_telemetry(v)
            return sanitized
        elif isinstance(data, list):
            return [SimulationDiagnosticEngine.sanitize_telemetry(item) for item in data]
        return data

    @classmethod
    def _build_diagnostic(
        cls,
        classification: str,
        remote_status: str,
        portfolio_state: str,
        metrics_state: str,
        diagnostic_code: str,
        root_cause_type: str,
        confidence: str,
        root_cause_message: str,
        why_not_proven: Optional[str] = None,
        observed: Optional[List[str]] = None,
        proven: Optional[List[str]] = None,
        inferred: Optional[List[str]] = None,
        possible: Optional[List[str]] = None,
        unknown: Optional[List[str]] = None,
        simulation_id: Optional[str] = None,
        brain_sim_id: Optional[str] = None,
        expression: str = "",
        settings_dict: Optional[Dict[str, Any]] = None,
        http_status: int = 200,
        position_count: Optional[int] = None,
        long_count: Optional[int] = None,
        short_count: Optional[int] = None,
        sharpe: Optional[float] = None,
        fitness: Optional[float] = None,
        turnover: Optional[float] = None,
        margin_bps: Optional[float] = None,
        returns: Optional[float] = None,
        drawdown: Optional[float] = None,
        component_tests: Optional[List[Dict[str, Any]]] = None,
        signal_stats: Optional[Dict[str, Any]] = None,
        position_pipeline: Optional[Dict[str, Any]] = None,
        recommended_experiments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        settings_dict = settings_dict or {}
        sim_id_str = simulation_id or "SIM-LOCAL"
        brain_id_str = brain_sim_id or "N/A"

        all_evidence = (observed or []) + (proven or []) + (inferred or [])

        from backend.app.generation.ast_parser import ExpressionASTParser
        expr_hash = ExpressionASTParser.compute_expression_hash(expression) if expression else "N/A"
        root_node = ExpressionASTParser.parse(expression) if expression else None

        expression_analysis = {
            "expression": expression,
            "expression_hash": expr_hash,
            "root": {
                "operator": root_node.name if root_node else "",
                "category": root_node.category() if root_node else ""
            },
            "components": component_tests or []
        }

        result = {
            "simulation_id": sim_id_str,
            "brain_sim_id": brain_id_str,
            "expression": expression,
            "expression_hash": expr_hash,
            "expression_analysis": expression_analysis,
            "http_status": http_status,
            "classification": classification,
            "remote_status": remote_status,
            "portfolio_state": portfolio_state,
            "portfolio_status": portfolio_state,
            "metrics_state": metrics_state,
            "metrics_status": "AVAILABLE" if metrics_state == "AVAILABLE" else "MISSING",
            "diagnostic_code": diagnostic_code,
            "position_count": position_count,
            "long_count": long_count,
            "short_count": short_count,
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "margin_bps": margin_bps,
            "returns_annualized": returns,
            "drawdown_max": drawdown,
            "has_valid_metrics": bool(metrics_state == "AVAILABLE" and sharpe is not None),
            "root_cause": {
                "type": root_cause_type,
                "confidence": confidence,
                "message": root_cause_message,
                "why_not_proven": why_not_proven,
                "evidence": all_evidence
            },
            "evidence_categorized": {
                "observed": observed or [],
                "proven": proven or [],
                "inferred": inferred or [],
                "possible": possible or [],
                "unknown": unknown or []
            },
            "diagnostic_reason": root_cause_message,
            "possible_cause": root_cause_message,
            "why_not_proven": why_not_proven,
            "evidence": all_evidence,
            "component_tests": component_tests or [],
            "signal_stats": signal_stats or {},
            "position_pipeline": position_pipeline or {},
            "recommended_experiments": recommended_experiments or [],
            "configuration": {
                "universe": settings_dict.get("universe", "TOP3000"),
                "region": settings_dict.get("region", "USA"),
                "delay": settings_dict.get("delay", 1),
                "neutralization": settings_dict.get("neutralization", "SUBINDUSTRY"),
                "truncation": settings_dict.get("truncation", 0.08)
            }
        }

        # Print structured ASCII diagnostic telemetry banner to log (Phase 24)
        cls._log_diagnostic_telemetry(result, expression)
        return result

    @classmethod
    def _log_diagnostic_telemetry(cls, d: Dict[str, Any], expression: str):
        cfg = d.get("configuration", {})
        root = d.get("root_cause", {})
        ev_cat = d.get("evidence_categorized", {})
        pipe = d.get("position_pipeline", {})

        obs_lines = "\n".join([f"  [OBSERVED] {e}" for e in ev_cat.get("observed", [])])
        prov_lines = "\n".join([f"  [PROVEN]   {e}" for e in ev_cat.get("proven", [])])
        inf_lines = "\n".join([f"  [INFERRED] {e}" for e in ev_cat.get("inferred", [])])
        unk_lines = "\n".join([f"  [UNKNOWN]  {e}" for e in ev_cat.get("unknown", [])])

        why_not_str = d.get("why_not_proven")
        why_not_block = f"\nWhy Not Proven:\n{why_not_str}\n" if why_not_str else ""

        comps = d.get("component_tests", [])
        comp_lines = "\n".join([f"  {idx+1}. {c['expression']}\n     ({c['stage']}) -> {c['status']}" for idx, c in enumerate(comps)])

        banner = f"""
========================================================
PORTFOLIO EMPTY DIAGNOSTIC (EVIDENCE-BASED)
========================================================

Simulation ID: {d.get('simulation_id')}
BRAIN ID: {d.get('brain_sim_id')}

Expression:
{expression}
Expression Hash: {d.get('expression_hash')}

AST Component Hierarchy:
{comp_lines}

Configuration:
Universe: {cfg.get('universe')}
Region: {cfg.get('region')}
Delay: {cfg.get('delay')}
Neutralization: {cfg.get('neutralization')}

Remote Status: {d.get('remote_status')}
HTTP Status: {d.get('http_status')}

Portfolio Status: {d.get('portfolio_state')}
Position Count: {d.get('position_count', 0)}
Metrics Status: {d.get('metrics_state')}

Primary Classification: {d.get('classification')}
Most Likely Hypothesis: {root.get('type')}
Confidence: {root.get('confidence')}

Categorized Evidence:
{obs_lines}
{prov_lines}
{inf_lines}
{unk_lines}
{why_not_block}
Position Pipeline:
Last Nonzero Stage: {pipe.get('last_nonzero_stage', 'NOT_OBSERVABLE')}

========================================================
"""
        verde_logger.log_event(
            event=f"DIAGNOSTIC_{d.get('classification')}",
            severity="INFO" if d.get('classification') == 'VALID_METRICS' else "WARNING",
            component="SIMULATION_DIAGNOSTICS",
            candidate_id=d.get('simulation_id'),
            message=f"Simulation Diagnostic evaluated: {d.get('classification')} ({root.get('type')} - Confidence {root.get('confidence')})",
            metadata={"classification": d.get("classification"), "root_cause": root.get("type"), "confidence": root.get("confidence")}
        )
        print(banner)


simulation_diagnostics = SimulationDiagnosticEngine()
