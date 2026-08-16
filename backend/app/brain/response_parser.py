from typing import Any, Dict, Optional
from backend.app.core.logging import verde_logger
from backend.app.research.diagnostics import simulation_diagnostics


class BrainResponseParser:
    """
    Parses raw WorldQuant BRAIN simulation responses.
    Strictly differentiates:
      - VALID_METRICS / SUCCESS
      - PORTFOLIO_EMPTY (simulation completed, but no positions taken)
      - METRICS_UNAVAILABLE (metrics absent because portfolio was empty)
      - ALPHA_FAILURE (syntax error, unsupported operator, constant signal)
      - REMOTE_FAILURE (HTTP 429/500/timeout)
      - AUTH_FAILURE (HTTP 401/403)
      - PARSER_FAILURE (malformed JSON / unexpected schema)
    NEVER converts missing metrics to 0.0 or fabricates metrics.
    """

    @staticmethod
    def parse_simulation_response(
        data: Any,
        expression: str = "",
        settings_dict: Optional[Dict[str, Any]] = None,
        http_status: int = 200,
        simulation_id: Optional[str] = None,
        brain_sim_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses simulation output from WorldQuant BRAIN using the SimulationDiagnosticEngine.
        """
        if not isinstance(data, dict):
            return {
                "classification": "PARSER_FAILURE",
                "remote_status": "PARSE_ERROR",
                "portfolio_state": "UNKNOWN",
                "portfolio_status": "UNKNOWN",
                "metrics_state": "PARSE_ERROR",
                "metrics_status": "PARSE_ERROR",
                "diagnostic_code": "INVALID_RESPONSE_TYPE",
                "sharpe": None,
                "fitness": None,
                "turnover": None,
                "margin_bps": None,
                "returns_annualized": None,
                "drawdown_max": None,
                "long_count": None,
                "short_count": None,
                "position_count": 0,
                "diagnostic_reason": "Invalid response payload format (non-dictionary received)",
                "possible_cause": "BRAIN remote API returned unexpected content or invalid JSON",
                "has_valid_metrics": False,
                "root_cause": {
                    "type": "RESPONSE_SCHEMA_MISMATCH",
                    "confidence": "HIGH",
                    "message": "Expected JSON dictionary response from BRAIN endpoint.",
                    "evidence": [f"Received data of type: {type(data).__name__}"]
                },
                "evidence": [f"Received non-dictionary data type: {type(data).__name__}"],
                "component_tests": [],
                "signal_stats": {}
            }

        return simulation_diagnostics.diagnose_simulation(
            raw_response=data,
            expression=expression or data.get("expression") or "",
            settings_dict=settings_dict or {},
            http_status=http_status,
            simulation_id=simulation_id,
            brain_sim_id=brain_sim_id or data.get("id") or data.get("simulation_id")
        )


response_parser = BrainResponseParser()
