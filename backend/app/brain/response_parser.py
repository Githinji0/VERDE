from typing import Any, Dict, Optional, Tuple
from backend.app.core.logging import verde_logger


class BrainResponseParser:
    """
    Parses raw WorldQuant BRAIN simulation responses.
    Strictly differentiates TECHNICAL_FAILURE (empty portfolio, missing metrics, parser failure)
    from true ALPHA_FAILURE (valid low Sharpe, high turnover).
    NEVER converts missing metrics to 0.0.
    """

    @staticmethod
    def parse_simulation_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses simulation output from WorldQuant BRAIN.
        
        Returns:
            {
                "classification": "VALID_METRICS" | "TECHNICAL_FAILURE" | "ALPHA_FAILURE",
                "portfolio_status": "VALID" | "EMPTY" | "UNKNOWN",
                "metrics_status": "AVAILABLE" | "MISSING" | "PARSE_ERROR",
                "sharpe": float | None,
                "fitness": float | None,
                "turnover": float | None,
                "margin_bps": float | None,
                "returns_annualized": float | None,
                "drawdown_max": float | None,
                "long_count": int | None,
                "short_count": int | None,
                "diagnostic_reason": str | None,
                "possible_cause": str | None,
                "has_valid_metrics": bool
            }
        """
        if not isinstance(data, dict):
            return {
                "classification": "TECHNICAL_FAILURE",
                "portfolio_status": "UNKNOWN",
                "metrics_status": "PARSE_ERROR",
                "sharpe": None,
                "fitness": None,
                "turnover": None,
                "margin_bps": None,
                "returns_annualized": None,
                "drawdown_max": None,
                "long_count": None,
                "short_count": None,
                "diagnostic_reason": "Invalid response payload format (non-dictionary received)",
                "possible_cause": "BRAIN remote API returned unexpected content",
                "has_valid_metrics": False
            }

        # Check for remote error/exception in response
        if "error" in data or "message" in data and not data.get("records"):
            err_msg = data.get("error") or data.get("message") or "Remote error"
            return {
                "classification": "TECHNICAL_FAILURE",
                "portfolio_status": "EMPTY",
                "metrics_status": "MISSING",
                "sharpe": None,
                "fitness": None,
                "turnover": None,
                "margin_bps": None,
                "returns_annualized": None,
                "drawdown_max": None,
                "long_count": None,
                "short_count": None,
                "diagnostic_reason": f"BRAIN returned error message: {err_msg}",
                "possible_cause": "Remote compilation, syntax, or execution failure in BRAIN engine",
                "has_valid_metrics": False
            }

        # Check for portfolio summary/metrics block
        # BRAIN returns metrics in records/summary/pnl/returns/stats
        records = data.get("records") or data.get("pnl") or data.get("result")
        stats = data.get("stats") or data.get("summary") or {}
        
        # Check if portfolio is empty (zero trades, zero positions, or empty PnL)
        pnl_records = data.get("records", [])
        if isinstance(pnl_records, list) and len(pnl_records) == 0 and not stats:
            return {
                "classification": "TECHNICAL_FAILURE",
                "portfolio_status": "EMPTY",
                "metrics_status": "MISSING",
                "sharpe": None,
                "fitness": None,
                "turnover": None,
                "margin_bps": None,
                "returns_annualized": None,
                "drawdown_max": None,
                "long_count": None,
                "short_count": None,
                "diagnostic_reason": "Simulation completed but portfolio is empty (no positions taken).",
                "possible_cause": "Alpha expression produced constant or identical values across all instruments.",
                "has_valid_metrics": False
            }

        # Extract numeric metrics if present
        def get_float(val: Any) -> Optional[float]:
            if val is None or val == "" or val == "N/A" or val == "null":
                return None
            try:
                f = float(val)
                if f != f:  # NaN check
                    return None
                return f
            except (ValueError, TypeError):
                return None

        # Look in stats or root dict
        sharpe = get_float(stats.get("sharpe") or data.get("sharpe"))
        fitness = get_float(stats.get("fitness") or data.get("fitness"))
        turnover = get_float(stats.get("turnover") or data.get("turnover"))
        margin_bps = get_float(stats.get("margin") or data.get("margin") or stats.get("margin_bps"))
        returns = get_float(stats.get("returns") or stats.get("pnl") or data.get("returns"))
        drawdown = get_float(stats.get("drawdown") or stats.get("max_drawdown") or data.get("drawdown"))
        long_count = stats.get("longCount") if stats.get("longCount") is not None else data.get("longCount")
        short_count = stats.get("shortCount") if stats.get("shortCount") is not None else data.get("shortCount")

        # Determine if metrics exist
        if sharpe is None or fitness is None:
            # Check if empty portfolio was the cause
            is_empty = (
                (long_count == 0 and short_count == 0) or
                (isinstance(pnl_records, list) and len(pnl_records) == 0 and (long_count is None or long_count == 0))
            )
            portfolio_status = "EMPTY" if is_empty else "UNKNOWN"
            return {
                "classification": "TECHNICAL_FAILURE",
                "portfolio_status": portfolio_status,
                "metrics_status": "MISSING",
                "sharpe": None,
                "fitness": None,
                "turnover": turnover,
                "margin_bps": margin_bps,
                "returns_annualized": returns,
                "drawdown_max": drawdown,
                "long_count": long_count,
                "short_count": short_count,
                "diagnostic_reason": "Portfolio metrics (Sharpe/Fitness) are missing or undefined.",
                "possible_cause": "Insufficient trades, constant signal, or unhandled data lookback issues.",
                "has_valid_metrics": False
            }

        # Valid metrics extracted successfully!
        return {
            "classification": "VALID_METRICS",
            "portfolio_status": "VALID",
            "metrics_status": "AVAILABLE",
            "sharpe": round(sharpe, 4),
            "fitness": round(fitness, 4),
            "turnover": round(turnover, 4) if turnover is not None else None,
            "margin_bps": round(margin_bps, 2) if margin_bps is not None else None,
            "returns_annualized": round(returns, 4) if returns is not None else None,
            "drawdown_max": round(drawdown, 4) if drawdown is not None else None,
            "long_count": int(long_count) if long_count is not None else None,
            "short_count": int(short_count) if short_count is not None else None,
            "diagnostic_reason": None,
            "possible_cause": None,
            "has_valid_metrics": True
        }


response_parser = BrainResponseParser()
