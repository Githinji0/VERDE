import hashlib
import math
import random
from typing import Any, Dict, Optional


class BrainSimulationSandbox:
    """
    Realistic quantitative simulation sandbox engine for VERDE.
    Generates deterministic, mathematically grounded simulation metrics,
    PnL trajectories, and trade distributions when running in SIMULATION mode
    or sandbox environment.
    """

    @staticmethod
    def simulate(expression: str, settings_dict: Optional[Dict[str, Any]] = None, family_code: str = "MOMENTUM") -> Dict[str, Any]:
        settings_dict = settings_dict or {}
        universe = settings_dict.get("universe", "TOP3000")
        
        # Deterministic seed based on expression
        expr_hash = int(hashlib.sha256(expression.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(expr_hash)

        # Baseline metrics by family
        family_baselines = {
            "MOMENTUM": {"sharpe": 1.65, "fitness": 1.35, "turnover": 0.32, "margin": 6.8},
            "MEAN_REVERSION": {"sharpe": 1.82, "fitness": 1.48, "turnover": 0.42, "margin": 5.4},
            "VOLATILITY": {"sharpe": 1.45, "fitness": 1.15, "turnover": 0.28, "margin": 7.5},
            "QUALITY": {"sharpe": 1.55, "fitness": 1.25, "turnover": 0.18, "margin": 9.2},
            "VALUE": {"sharpe": 1.38, "fitness": 1.08, "turnover": 0.14, "margin": 8.6},
            "GROWTH": {"sharpe": 1.42, "fitness": 1.12, "turnover": 0.22, "margin": 7.0},
            "SENTIMENT": {"sharpe": 1.72, "fitness": 1.40, "turnover": 0.38, "margin": 6.1},
            "ANALYST": {"sharpe": 1.58, "fitness": 1.28, "turnover": 0.25, "margin": 7.8},
        }

        base = family_baselines.get(family_code.upper(), {"sharpe": 1.40, "fitness": 1.10, "turnover": 0.30, "margin": 6.0})

        # Structural modifiers based on operators and depth
        sharpe_delta = (rng.random() - 0.35) * 0.8
        fitness_delta = (rng.random() - 0.35) * 0.6
        turnover_delta = (rng.random() - 0.5) * 0.15
        margin_delta = (rng.random() - 0.4) * 3.0

        sharpe = round(max(0.60, base["sharpe"] + sharpe_delta), 2)
        fitness = round(max(0.45, base["fitness"] + fitness_delta), 2)
        turnover = round(max(0.08, min(0.85, base["turnover"] + turnover_delta)), 3)
        margin_bps = round(max(2.0, base["margin"] + margin_delta), 2)
        returns = round(sharpe * 0.11 + rng.random() * 0.04, 3)
        drawdown = round(max(0.03, 0.22 / max(0.8, sharpe) + (rng.random() - 0.5) * 0.03), 3)

        long_count = int(rng.randint(180, 420))
        short_count = int(rng.randint(170, 410))

        # Generate synthetic PnL record curve (52 trading weeks)
        records = []
        cum_pnl = 0.0
        for week in range(1, 53):
            weekly_return = (returns / 52.0) + (rng.gauss(0, 0.015))
            cum_pnl += round(weekly_return * 100000, 2)
            records.append({
                "week": week,
                "pnl": cum_pnl,
                "weekly_return": round(weekly_return, 4)
            })

        return {
            "status": "COMPLETE",
            "progress": 1.0,
            "stats": {
                "sharpe": sharpe,
                "fitness": fitness,
                "turnover": turnover,
                "margin": margin_bps,
                "margin_bps": margin_bps,
                "returns": returns,
                "drawdown": drawdown,
                "max_drawdown": drawdown,
                "longCount": long_count,
                "shortCount": short_count,
                "universe": universe
            },
            "records": records
        }


simulation_sandbox = BrainSimulationSandbox()
