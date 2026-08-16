import pytest
from backend.app.generation.field_registry import FIELD_REGISTRY, get_field_metadata
from backend.app.generation.operator_registry import OPERATOR_REGISTRY, get_operator_metadata


def test_field_registry_categories_and_temporal():
    close_meta = get_field_metadata("close")
    assert close_meta["category"] == "PRICE"
    assert close_meta["temporal_behavior"] == "FAST"

    capex_meta = get_field_metadata("capex")
    assert capex_meta["category"] == "FUNDAMENTAL"
    assert capex_meta["temporal_behavior"] == "SLOW"
    assert "ts_mean" in capex_meta["discouraged_operators"]


def test_operator_registry_properties():
    rank_meta = get_operator_metadata("rank")
    assert rank_meta is not None
    assert rank_meta["arity"] == 1
    assert rank_meta["category"] == "CROSS_SECTIONAL"

    ts_mean_meta = get_operator_metadata("ts_mean")
    assert ts_mean_meta is not None
    assert ts_mean_meta["arity"] == 2
    assert ts_mean_meta["category"] == "TIME_SERIES"
