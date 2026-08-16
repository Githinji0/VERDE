from backend.app.generation.expression_builder import (
    ASTNode, BinaryOpNode, ConstantNode, FieldNode, GroupOpNode, SafeDivNode, TimeSeriesOpNode, UnaryOpNode
)


def safe_divide(numerator: ASTNode, denominator: ASTNode, epsilon: float = 0.0001) -> ASTNode:
    """Safely divides two expressions adding epsilon to prevent zero-division."""
    return SafeDivNode(numerator, denominator, epsilon)


def volatility_normalizer(signal: ASTNode, returns_field: str = "returns", lookback: int = 20) -> ASTNode:
    """Normalizes raw signal by rolling historical volatility: signal / ts_std_dev(returns, lookback)."""
    vol_node = TimeSeriesOpNode("ts_std_dev", FieldNode(returns_field), lookback)
    return safe_divide(signal, vol_node)


def smoothed_signal_engine(signal: ASTNode, lookback: int = 5) -> ASTNode:
    """Smooths raw signal with short rolling mean: ts_mean(signal, lookback)."""
    return TimeSeriesOpNode("ts_mean", signal, lookback)


def cross_sectional_rank(signal: ASTNode) -> ASTNode:
    """Applies cross-sectional rank: rank(signal)."""
    return UnaryOpNode("rank", signal)


def cross_sectional_zscore(signal: ASTNode) -> ASTNode:
    """Applies cross-sectional z-score: zscore(signal)."""
    return UnaryOpNode("zscore", signal)


def group_neutralize_signal(signal: ASTNode, group: str = "subindustry") -> ASTNode:
    """Neutralizes signal across specified industry group: group_neutralize(signal, group)."""
    return GroupOpNode("group_neutralize", signal, group)
