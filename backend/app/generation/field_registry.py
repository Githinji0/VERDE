from typing import Any, Dict, List, Optional

FIELD_REGISTRY: Dict[str, Dict[str, Any]] = {
    # PRICE FIELDS (FAST)
    "close": {
        "name": "close",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["MOMENTUM", "MEAN_REVERSION", "VOLATILITY", "VALUE", "PRICE_ACTION", "MICROSTRUCTURE", "COMPOSITE"],
        "preferred_operators": ["ts_delta", "ts_delay", "ts_mean", "ts_rank", "ts_zscore", "rank"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5, 10, 20, 60, 120, 252],
        "data_quality": 1.0,
        "notes": "Daily closing price adjusted for splits and dividends."
    },
    "open": {
        "name": "open",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["PRICE_ACTION", "MOMENTUM", "MEAN_REVERSION"],
        "preferred_operators": ["subtract", "divide", "rank"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5],
        "data_quality": 1.0,
        "notes": "Daily opening price."
    },
    "high": {
        "name": "high",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["PRICE_ACTION", "VOLATILITY", "MEAN_REVERSION"],
        "preferred_operators": ["subtract", "divide", "ts_max", "rank"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5, 20],
        "data_quality": 1.0,
        "notes": "Daily high price."
    },
    "low": {
        "name": "low",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["PRICE_ACTION", "VOLATILITY", "MEAN_REVERSION"],
        "preferred_operators": ["subtract", "divide", "ts_min", "rank"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5, 20],
        "data_quality": 1.0,
        "notes": "Daily low price."
    },
    "vwap": {
        "name": "vwap",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["MICROSTRUCTURE", "PRICE_ACTION", "MEAN_REVERSION", "MOMENTUM"],
        "preferred_operators": ["subtract", "divide", "ts_zscore", "rank"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5, 10],
        "data_quality": 0.98,
        "notes": "Volume-weighted average price."
    },
    "returns": {
        "name": "returns",
        "category": "PRICE",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["MOMENTUM", "MEAN_REVERSION", "VOLATILITY", "CROSS_SECTIONAL"],
        "preferred_operators": ["ts_mean", "ts_std_dev", "ts_rank", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "recommended_horizons": [1, 5, 20, 60],
        "data_quality": 1.0,
        "notes": "Single-day percentage return."
    },

    # VOLUME & LIQUIDITY FIELDS (FAST / MEDIUM)
    "volume": {
        "name": "volume",
        "category": "VOLUME",
        "temporal_behavior": "FAST",
        "typical_frequency": "DAILY",
        "supported_families": ["VOLUME", "LIQUIDITY", "MICROSTRUCTURE"],
        "preferred_operators": ["ts_mean", "ts_zscore", "divide", "rank"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [5, 10, 20, 60],
        "data_quality": 1.0,
        "notes": "Daily trading volume in shares."
    },
    "shares_out": {
        "name": "shares_out",
        "category": "LIQUIDITY",
        "temporal_behavior": "SLOW",
        "typical_frequency": "MONTHLY",
        "supported_families": ["VALUE", "LIQUIDITY", "GROWTH"],
        "preferred_operators": ["multiply", "divide"],
        "discouraged_operators": ["ts_delta", "ts_std_dev"],
        "recommended_horizons": [60, 252],
        "data_quality": 0.95,
        "notes": "Total shares outstanding."
    },
    "turnover_ratio": {
        "name": "turnover_ratio",
        "category": "LIQUIDITY",
        "temporal_behavior": "MEDIUM",
        "typical_frequency": "DAILY",
        "supported_families": ["LIQUIDITY", "VOLUME"],
        "preferred_operators": ["ts_mean", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "recommended_horizons": [10, 20, 60],
        "data_quality": 0.95,
        "notes": "Daily volume divided by shares outstanding."
    },

    # FUNDAMENTAL FIELDS (SLOW - QUARTERLY)
    "capex": {
        "name": "capex",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["INVESTMENT", "QUALITY", "VALUE"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta", "ts_mean", "ts_std_dev", "ts_zscore"],
        "recommended_horizons": [63, 126, 252],
        "data_quality": 0.95,
        "notes": "Capital expenditures from cash flow statement. Slow moving quarterly metric."
    },
    "revenue": {
        "name": "revenue",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["GROWTH", "VALUE", "INVESTMENT", "PROFITABILITY"],
        "preferred_operators": ["ts_delay", "divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta", "ts_std_dev"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.98,
        "notes": "Total quarterly revenue."
    },
    "book_value": {
        "name": "book_value",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["VALUE", "QUALITY", "COMPOSITE"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta", "ts_mean", "ts_std_dev"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.98,
        "notes": "Common stockholders equity."
    },
    "operating_income": {
        "name": "operating_income",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["PROFITABILITY", "QUALITY", "GROWTH", "VALUE"],
        "preferred_operators": ["divide", "rank", "group_neutralize", "ts_delay"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.97,
        "notes": "Operating income / EBIT."
    },
    "net_income": {
        "name": "net_income",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["QUALITY", "GROWTH", "EARNINGS", "PROFITABILITY"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.97,
        "notes": "GAAP Net income."
    },
    "operating_cash_flow": {
        "name": "operating_cash_flow",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["QUALITY", "VALUE"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.96,
        "notes": "Cash flow from operations."
    },
    "free_cash_flow": {
        "name": "free_cash_flow",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["VALUE", "QUALITY"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.95,
        "notes": "Operating cash flow minus capex."
    },
    "total_assets": {
        "name": "total_assets",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["QUALITY", "PROFITABILITY", "LEVERAGE", "INVESTMENT"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta", "ts_mean"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.98,
        "notes": "Total assets on balance sheet."
    },
    "total_debt": {
        "name": "total_debt",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["LEVERAGE", "QUALITY"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.96,
        "notes": "Total short-term and long-term interest bearing debt."
    },
    "gross_profit": {
        "name": "gross_profit",
        "category": "FUNDAMENTAL",
        "temporal_behavior": "SLOW",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["PROFITABILITY", "QUALITY"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.98,
        "notes": "Revenue minus cost of goods sold."
    },

    # ESTIMATE & ANALYST FIELDS (EVENT_DRIVEN / MEDIUM)
    "eps": {
        "name": "eps",
        "category": "ESTIMATE",
        "temporal_behavior": "EVENT_DRIVEN",
        "typical_frequency": "QUARTERLY",
        "supported_families": ["EARNINGS", "GROWTH", "VALUE"],
        "preferred_operators": ["ts_delay", "divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_std_dev"],
        "recommended_horizons": [63, 252],
        "data_quality": 0.95,
        "notes": "Diluted earnings per share."
    },
    "target_price": {
        "name": "target_price",
        "category": "ESTIMATE",
        "temporal_behavior": "MEDIUM",
        "typical_frequency": "DAILY",
        "supported_families": ["ANALYST_ESTIMATES"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "recommended_horizons": [20, 60],
        "data_quality": 0.90,
        "notes": "Consensus 12-month analyst target price."
    },
    "est_revision_30d": {
        "name": "est_revision_30d",
        "category": "ESTIMATE",
        "temporal_behavior": "MEDIUM",
        "typical_frequency": "DAILY",
        "supported_families": ["ANALYST_ESTIMATES"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "recommended_horizons": [10, 30],
        "data_quality": 0.88,
        "notes": "Net upward minus downward consensus revisions over 30 days."
    }
}


def get_field_metadata(field_name: str) -> Dict[str, Any]:
    """Retrieve field metadata or default UNKNOWN definition."""
    clean = field_name.lower().strip()
    return FIELD_REGISTRY.get(clean, {
        "name": clean,
        "category": "UNKNOWN",
        "temporal_behavior": "UNKNOWN",
        "typical_frequency": "UNKNOWN",
        "supported_families": [],
        "preferred_operators": [],
        "discouraged_operators": [],
        "recommended_horizons": [20],
        "data_quality": 0.5,
        "notes": "Unregistered or custom BRAIN field."
    })
