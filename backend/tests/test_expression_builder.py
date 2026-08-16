import pytest
from backend.app.generation.expression_builder import (
    BinaryOpNode, ConstantNode, FieldNode, GroupOpNode, SafeDivNode, TimeSeriesOpNode, UnaryOpNode
)
from backend.app.generation.similarity import compute_expression_hash, compute_structure_hash
from backend.app.generation.transformations import (
    cross_sectional_rank, group_neutralize_signal, safe_divide, smoothed_signal_engine, volatility_normalizer
)


def test_ast_compiler_simple():
    node = UnaryOpNode("rank", FieldNode("close"))
    assert node.to_code() == "rank(close)"
    assert node.get_fields() == {"close"}
    assert node.get_operators() == {"rank"}


def test_ast_compiler_complex_tree():
    # group_neutralize(rank(capex / revenue), subindustry)
    div_node = SafeDivNode(FieldNode("capex"), FieldNode("revenue"))
    rank_node = UnaryOpNode("rank", div_node)
    group_node = GroupOpNode("group_neutralize", rank_node, "subindustry")

    compiled = group_node.to_code()
    assert "group_neutralize" in compiled
    assert "rank" in compiled
    assert "capex" in compiled
    assert "revenue" in compiled
    assert "subindustry" in compiled
    assert group_node.get_fields() == {"capex", "revenue"}


def test_safe_transformations():
    sig = FieldNode("close")
    norm_sig = volatility_normalizer(sig, "returns", 20)
    code = norm_sig.to_code()
    assert "ts_std_dev" in code
    assert "returns" in code


def test_expression_and_structure_hashing():
    expr1 = "rank(close / ts_delay(close, 20) - 1)"
    expr2 = "rank( close / ts_delay( close , 20 ) - 1 )"
    expr3 = "rank(close / ts_delay(close, 40) - 1)"

    assert compute_expression_hash(expr1) == compute_expression_hash(expr2)
    # Structure hash matches despite different lookback numbers
    assert compute_structure_hash(expr1) == compute_structure_hash(expr3)
