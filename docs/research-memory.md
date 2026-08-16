# Persistent Research Memory

VERDE maintains dynamic empirical performance matrices for:
- **Research Families** (`FamilyPerformance`)
- **Fields** (`FieldPerformance`)
- **Operators** (`OperatorPerformance`)

## Tracked Metrics
- `total_candidates`: Lifetime generation count
- `valid_simulations`: Count of simulations with full valid metrics
- `empty_portfolio_count`: Simulations resulting in empty portfolios
- `empty_portfolio_rate`: `empty_portfolio_count / total_candidates`
- `avg_sharpe`: Rolling average Sharpe across valid simulations only
- `avg_fitness`: Rolling average Fitness across valid simulations only
- `success_rate`: `valid_simulations / total_candidates`

## Adaptive Feedback
High-empty-rate fields or low-performing operator pairs are adaptively down-weighted during subsequent generation cycles.
