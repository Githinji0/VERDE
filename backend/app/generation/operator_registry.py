from typing import Any, Dict, List, Optional

OPERATOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    # CROSS-SECTIONAL OPERATORS
    "rank": {
        "name": "rank",
        "category": "CROSS_SECTIONAL",
        "arity": 1,
        "accepted_arg_types": ["FIELD", "EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.0,
        "description": "Cross-sectional percentile rank across the entire universe (0.0 to 1.0)."
    },
    "zscore": {
        "name": "zscore",
        "category": "CROSS_SECTIONAL",
        "arity": 1,
        "accepted_arg_types": ["FIELD", "EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.2,
        "description": "Cross-sectional z-score (mean 0, std 1) across the universe."
    },
    "group_neutralize": {
        "name": "group_neutralize",
        "category": "GROUP",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "GROUP"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "MEDIUM",
        "complexity_cost": 1.5,
        "description": "Subtracts group-level mean from each asset signal (e.g. subindustry, sector)."
    },

    # TIME SERIES OPERATORS
    "ts_mean": {
        "name": "ts_mean",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "MEDIUM",
        "complexity_cost": 1.2,
        "description": "Rolling time-series mean over lookback days."
    },
    "ts_std_dev": {
        "name": "ts_std_dev",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "MEDIUM",
        "complexity_cost": 1.4,
        "description": "Rolling time-series standard deviation over lookback days."
    },
    "ts_delta": {
        "name": "ts_delta",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.1,
        "description": "Difference between current value and value 'd' days ago (x - ts_delay(x, d))."
    },
    "ts_delay": {
        "name": "ts_delay",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.0,
        "description": "Value of expression 'd' days ago."
    },
    "ts_rank": {
        "name": "ts_rank",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.5,
        "description": "Rolling time-series rank over lookback window (0.0 to 1.0)."
    },
    "ts_zscore": {
        "name": "ts_zscore",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.5,
        "description": "Rolling time-series z-score: (x - ts_mean(x, d)) / ts_std_dev(x, d)."
    },
    "ts_max": {
        "name": "ts_max",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.1,
        "description": "Rolling maximum value over lookback window."
    },
    "ts_min": {
        "name": "ts_min",
        "category": "TIME_SERIES",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "INTEGER"],
        "temporal_requirements": "TIME_SERIES",
        "lookback_requirements": "REQUIRED",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.1,
        "description": "Rolling minimum value over lookback window."
    },

    # MATHEMATICAL OPERATORS
    "log": {
        "name": "log",
        "category": "MATH",
        "arity": 1,
        "accepted_arg_types": ["EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.1,
        "description": "Natural logarithm (ln(x))."
    },
    "abs": {
        "name": "abs",
        "category": "MATH",
        "arity": 1,
        "accepted_arg_types": ["EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.0,
        "description": "Absolute value."
    },
    "sign": {
        "name": "sign",
        "category": "MATH",
        "arity": 1,
        "accepted_arg_types": ["EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "HIGH",
        "complexity_cost": 1.0,
        "description": "Sign of x (-1, 0, +1). High constant signal risk if applied naively."
    },
    "max": {
        "name": "max",
        "category": "MATH",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.0,
        "description": "Pairwise maximum."
    },
    "min": {
        "name": "min",
        "category": "MATH",
        "arity": 2,
        "accepted_arg_types": ["EXPR", "EXPR"],
        "temporal_requirements": "NONE",
        "lookback_requirements": "NONE",
        "constant_signal_risk": "LOW",
        "complexity_cost": 1.0,
        "description": "Pairwise minimum."
    }
}


def get_operator_metadata(op_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve operator metadata or None if unsupported."""
    return OPERATOR_REGISTRY.get(op_name.lower().strip())
