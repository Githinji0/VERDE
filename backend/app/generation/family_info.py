from typing import Any, Dict, List

RESEARCH_FAMILIES: Dict[str, Dict[str, Any]] = {
    "MOMENTUM": {
        "code": "MOMENTUM",
        "name": "Price & Trend Momentum",
        "description": "Exploits the tendency of assets with strong past performance to continue outperforming in the medium term.",
        "core_hypothesis": "Past relative price winners outperform past relative losers over medium horizons (20-60 trading days).",
        "preferred_fields": ["close", "returns", "vwap", "open", "high", "low"],
        "allowed_fields": ["close", "returns", "vwap", "volume", "high", "low"],
        "preferred_operators": ["ts_delta", "ts_delay", "ts_mean", "ts_rank", "ts_zscore", "rank"],
        "discouraged_operators": ["ts_std_dev"],
        "temporal_behavior": "FAST",
        "expected_horizon": "20-60d",
        "expected_turnover": "MEDIUM",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
        "templates": [
            "rank(close / ts_delay(close, {lookback}) - 1)",
            "rank(ts_delta(close, {lookback}) / ts_delay(close, {lookback}))",
            "group_neutralize(rank(ts_mean(returns, {lookback})), subindustry)",
            "rank(ts_rank(close, {lookback}))"
        ]
    },
    "MEAN_REVERSION": {
        "code": "MEAN_REVERSION",
        "name": "Short-Term Mean Reversion",
        "description": "Capitalizes on temporary overshooting and liquidity shocks that cause short-term price deviations from historical averages.",
        "core_hypothesis": "Extreme short-term price deviations from moving averages revert back toward equilibrium.",
        "preferred_fields": ["close", "vwap", "returns", "high", "low"],
        "allowed_fields": ["close", "vwap", "returns", "volume", "high", "low"],
        "preferred_operators": ["ts_mean", "ts_zscore", "ts_delta", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "FAST",
        "expected_horizon": "1-10d",
        "expected_turnover": "HIGH",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "rank(-(close - ts_mean(close, {lookback})))",
            "rank(-ts_zscore(close, {lookback}))",
            "group_neutralize(rank(-(close / ts_mean(close, {lookback}) - 1)), subindustry)"
        ]
    },
    "VALUE": {
        "code": "VALUE",
        "name": "Fundamental Valuation",
        "description": "Identifies undervalued securities relative to their fundamental accounting metrics such as book value, cash flow, and earnings.",
        "core_hypothesis": "Firms with high fundamental yields (book-to-price, cash flow-to-price) generate long-term risk-adjusted excess returns.",
        "preferred_fields": ["book_value", "free_cash_flow", "operating_cash_flow", "enterprise_value", "sales", "close"],
        "allowed_fields": ["book_value", "free_cash_flow", "operating_cash_flow", "sales", "earnings", "close", "market_cap"],
        "preferred_operators": ["divide", "rank", "group_neutralize", "ts_mean"],
        "discouraged_operators": ["ts_delta", "ts_std_dev"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "LOW",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(book_value / (close * shares_out)), subindustry)",
            "rank(free_cash_flow / enterprise_value)",
            "group_neutralize(rank(operating_cash_flow / (close * shares_out)), sector)"
        ]
    },
    "QUALITY": {
        "code": "QUALITY",
        "name": "Balance Sheet & Earnings Quality",
        "description": "Prefers firms with stable, cash-backed earnings, high accounting integrity, and low accruals over low-quality firms.",
        "core_hypothesis": "High-quality balance sheets with strong cash conversion deliver superior risk-adjusted durability.",
        "preferred_fields": ["operating_income", "total_assets", "net_income", "operating_cash_flow", "accruals"],
        "allowed_fields": ["operating_income", "total_assets", "net_income", "operating_cash_flow", "accruals", "total_debt"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "rank((operating_cash_flow - net_income) / total_assets)",
            "group_neutralize(rank(operating_income / total_assets), subindustry)"
        ]
    },
    "GROWTH": {
        "code": "GROWTH",
        "name": "Fundamental Growth & Acceleration",
        "description": "Captures sustained expansion in corporate revenues, operating earnings, and free cash flows across multi-period windows.",
        "core_hypothesis": "Companies demonstrating accelerating top-line and bottom-line growth command superior fundamental re-ratings.",
        "preferred_fields": ["revenue", "operating_income", "net_income", "eps"],
        "allowed_fields": ["revenue", "operating_income", "net_income", "eps", "ebitda"],
        "preferred_operators": ["ts_delay", "divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_std_dev"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(revenue / ts_delay(revenue, 252) - 1), subindustry)",
            "rank((operating_income - ts_delay(operating_income, 252)) / total_assets)"
        ]
    },
    "VOLATILITY": {
        "code": "VOLATILITY",
        "name": "Volatility & Idiosyncratic Risk",
        "description": "Exploits the low-volatility anomaly and mispricing in idiosyncratic risk across equities.",
        "core_hypothesis": "Lower-volatility equities deliver higher risk-adjusted Sharpe ratios due to leverage and benchmark constraints.",
        "preferred_fields": ["returns", "close", "high", "low"],
        "allowed_fields": ["returns", "close", "high", "low", "volume"],
        "preferred_operators": ["ts_std_dev", "ts_mean", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "MEDIUM",
        "expected_horizon": "20-60d",
        "expected_turnover": "LOW-MED",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "rank(-ts_std_dev(returns, {lookback}))",
            "group_neutralize(rank(-ts_std_dev(returns, {lookback}) / ts_mean(returns, {lookback})), subindustry)"
        ]
    },
    "LIQUIDITY": {
        "code": "LIQUIDITY",
        "name": "Liquidity & Market Friction",
        "description": "Harvests liquidity premia by evaluating bid-ask spreads, turnover ratios, and trading friction.",
        "core_hypothesis": "Illiquid or friction-heavy assets trade at structural discounts that revert over medium horizons.",
        "preferred_fields": ["volume", "close", "turnover_ratio", "shares_out"],
        "allowed_fields": ["volume", "close", "turnover_ratio", "shares_out", "vwap"],
        "preferred_operators": ["ts_mean", "divide", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "FAST-MED",
        "expected_horizon": "10-40d",
        "expected_turnover": "MED",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(-(volume * close) / (close * shares_out)), subindustry)",
            "rank(-ts_mean(volume, {lookback}) / shares_out)"
        ]
    },
    "VOLUME": {
        "code": "VOLUME",
        "name": "Volume Dynamics & Order Pressure",
        "description": "Measures abnormal volume surges, volume-weighted trend persistence, and accumulation/distribution signals.",
        "core_hypothesis": "Volume precedes price; unusual volume concentration in the direction of trend indicates institutional accumulation.",
        "preferred_fields": ["volume", "close", "vwap", "returns"],
        "allowed_fields": ["volume", "close", "vwap", "returns", "open", "high", "low"],
        "preferred_operators": ["ts_mean", "divide", "ts_zscore", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "FAST",
        "expected_horizon": "5-20d",
        "expected_turnover": "MED-HIGH",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "rank((volume / ts_mean(volume, {lookback})) * returns)",
            "group_neutralize(rank(ts_zscore(volume, {lookback}) * (close - vwap)), subindustry)"
        ]
    },
    "INVESTMENT": {
        "code": "INVESTMENT",
        "name": "Corporate Investment & Capital Intensity",
        "description": "Evaluates capital expenditure discipline; penalizes aggressive empire-building and rewards disciplined capital allocators.",
        "core_hypothesis": "Firms with moderate, high-return capex outperform firms with aggressive asset expansion and dilutive capex.",
        "preferred_fields": ["capex", "revenue", "total_assets", "depreciation", "net_income"],
        "allowed_fields": ["capex", "revenue", "total_assets", "depreciation", "net_income", "pp_and_e"],
        "preferred_operators": ["divide", "rank", "group_neutralize", "subtract"],
        "discouraged_operators": ["ts_delta", "ts_std_dev"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(-capex / revenue), subindustry)",
            "group_neutralize(rank(-capex / total_assets), sector)"
        ]
    },
    "LEVERAGE": {
        "code": "LEVERAGE",
        "name": "Financial Leverage & Solvency",
        "description": "Assesses balance sheet distress, debt burdens, interest coverage, and default vulnerability.",
        "core_hypothesis": "Overleveraged firms facing credit contraction underperform low-debt, high-coverage peers.",
        "preferred_fields": ["total_debt", "total_assets", "operating_income", "interest_expense", "cash_and_equiv"],
        "allowed_fields": ["total_debt", "total_assets", "operating_income", "interest_expense", "cash_and_equiv", "book_value"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(-(total_debt - cash_and_equiv) / total_assets), subindustry)",
            "rank(operating_income / interest_expense)"
        ]
    },
    "PROFITABILITY": {
        "code": "PROFITABILITY",
        "name": "Capital Efficiency & Operating Margins",
        "description": "Measures return on equity (ROE), return on invested capital (ROIC), and gross margins.",
        "core_hypothesis": "Firms with sustainable economic moats generate higher operating margins and return on equity.",
        "preferred_fields": ["gross_profit", "operating_income", "total_assets", "book_value", "revenue"],
        "allowed_fields": ["gross_profit", "operating_income", "total_assets", "book_value", "revenue", "net_income"],
        "preferred_operators": ["divide", "rank", "group_neutralize"],
        "discouraged_operators": ["ts_delta"],
        "temporal_behavior": "SLOW",
        "expected_horizon": "60-250d",
        "expected_turnover": "LOW",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "group_neutralize(rank(gross_profit / total_assets), subindustry)",
            "rank(operating_income / revenue)"
        ]
    },
    "EARNINGS": {
        "code": "EARNINGS",
        "name": "Earnings Surprises & Momentum",
        "description": "Captures post-earnings announcement drift (PEAD) and positive earnings surprise persistence.",
        "core_hypothesis": "Stock prices underreact to unexpected earnings surprises, leading to predictable drift.",
        "preferred_fields": ["eps", "net_income", "operating_income", "close"],
        "allowed_fields": ["eps", "net_income", "operating_income", "close", "revenue"],
        "preferred_operators": ["ts_delay", "divide", "subtract", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "EVENT_DRIVEN",
        "expected_horizon": "20-60d",
        "expected_turnover": "MED",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "group_neutralize(rank((eps - ts_delay(eps, 252)) / close), subindustry)",
            "rank((net_income - ts_delay(net_income, 63)) / total_assets)"
        ]
    },
    "ANALYST_ESTIMATES": {
        "code": "ANALYST_ESTIMATES",
        "name": "Consensus Revisions & Target Price",
        "description": "Tracks institutional analyst revisions in forward EPS, revenue forecasts, and target prices.",
        "core_hypothesis": "Upward revisions by sell-side analysts signal institutional conviction and upcoming positive flows.",
        "preferred_fields": ["target_price", "consensus_eps_est", "est_revision_30d", "close"],
        "allowed_fields": ["target_price", "consensus_eps_est", "est_revision_30d", "close", "recommendation_mean"],
        "preferred_operators": ["divide", "subtract", "rank", "group_neutralize", "ts_delta"],
        "discouraged_operators": [],
        "temporal_behavior": "MEDIUM",
        "expected_horizon": "20-60d",
        "expected_turnover": "MED",
        "complexity_range": "MED",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank((target_price - close) / close), subindustry)",
            "rank(est_revision_30d / close)"
        ]
    },
    "PRICE_ACTION": {
        "code": "PRICE_ACTION",
        "name": "Intraday & Technical Geometry",
        "description": "Extracts directional pressure from intraday candlesticks, shadows, ranges, and gap openings.",
        "core_hypothesis": "Opening gaps and high-low range expansions reveal asymmetric institutional order flow.",
        "preferred_fields": ["open", "close", "high", "low", "vwap"],
        "allowed_fields": ["open", "close", "high", "low", "vwap", "volume"],
        "preferred_operators": ["subtract", "divide", "ts_mean", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "FAST",
        "expected_horizon": "1-10d",
        "expected_turnover": "HIGH",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY"],
        "templates": [
            "rank((close - open) / (high - low + 0.0001))",
            "group_neutralize(rank((close - vwap) / (high - low + 0.0001)), subindustry)"
        ]
    },
    "MICROSTRUCTURE": {
        "code": "MICROSTRUCTURE",
        "name": "VWAP Benchmark & Execution Frictions",
        "description": "Exploits short-horizon price dislocations relative to VWAP benchmarks and order imbalances.",
        "core_hypothesis": "Short-term divergence from daily volume-weighted average price (VWAP) mean-reverts intraday/next-day.",
        "preferred_fields": ["close", "vwap", "volume", "returns"],
        "allowed_fields": ["close", "vwap", "volume", "returns", "open"],
        "preferred_operators": ["subtract", "divide", "ts_zscore", "rank", "group_neutralize"],
        "discouraged_operators": [],
        "temporal_behavior": "FAST",
        "expected_horizon": "1-5d",
        "expected_turnover": "HIGH",
        "complexity_range": "LOW-MED",
        "neutralization_options": ["SUBINDUSTRY"],
        "templates": [
            "rank(-(close - vwap) / vwap)",
            "group_neutralize(rank(-ts_zscore(close - vwap, 10)), subindustry)"
        ]
    },
    "CROSS_SECTIONAL": {
        "code": "CROSS_SECTIONAL",
        "name": "Cross-Sectional Relative Strength",
        "description": "Evaluates normalized relative ranking of multiple factors simultaneously within granular industry peer groups.",
        "core_hypothesis": "Multi-factor relative cross-sectional ranking eliminates sector bias and generates stable long/short spreads.",
        "preferred_fields": ["returns", "volume", "operating_cash_flow", "close"],
        "allowed_fields": ["returns", "volume", "operating_cash_flow", "book_value", "close", "sales"],
        "preferred_operators": ["rank", "group_neutralize", "ts_mean", "zscore"],
        "discouraged_operators": [],
        "temporal_behavior": "MEDIUM",
        "expected_horizon": "10-60d",
        "expected_turnover": "MED",
        "complexity_range": "MED-HIGH",
        "neutralization_options": ["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(rank(returns / ts_std_dev(returns, 20)), subindustry)",
            "group_neutralize(rank(book_value / (close * shares_out)) + rank(operating_cash_flow / total_assets), industry)"
        ]
    },
    "COMPOSITE": {
        "code": "COMPOSITE",
        "name": "Multi-Factor Ensemble & Synthesis",
        "description": "Combines orthogonal factor signals (e.g. Value + Momentum + Quality) to minimize regime drawdowns.",
        "core_hypothesis": "Combining lowly-correlated alpha families produces smoother PnL curves and higher overall Sharpe ratios.",
        "preferred_fields": ["close", "book_value", "operating_income", "returns", "total_assets"],
        "allowed_fields": ["close", "book_value", "operating_income", "returns", "total_assets", "volume", "revenue"],
        "preferred_operators": ["rank", "group_neutralize", "add", "multiply", "ts_mean"],
        "discouraged_operators": [],
        "temporal_behavior": "MEDIUM",
        "expected_horizon": "20-120d",
        "expected_turnover": "LOW-MED",
        "complexity_range": "HIGH",
        "neutralization_options": ["SUBINDUSTRY", "SECTOR"],
        "templates": [
            "group_neutralize(0.5 * rank(close / ts_delay(close, 60) - 1) + 0.5 * rank(book_value / (close * shares_out)), subindustry)",
            "group_neutralize(rank(operating_income / total_assets) + rank(-ts_std_dev(returns, 20)), sector)"
        ]
    }
}
