import pytest
from backend.app.brain.payloads import build_simulation_payload
from backend.app.core.exceptions import BrainPayloadException


def test_build_simulation_payload_valid():
    expr = "rank(close / ts_delay(close, 20) - 1)"
    settings = {
        "universe": "TOP3000",
        "region": "USA",
        "delay": 1,
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
        "truncation": 0.08,
        "pasteurization": "ON",
        "language": "FASTEXPR"
    }

    payload = build_simulation_payload(expr, settings)
    assert payload["type"] == "REGULAR"
    assert payload["regular"] == expr
    assert payload["settings"]["universe"] == "TOP3000"
    assert payload["settings"]["region"] == "USA"
    assert payload["settings"]["neutralization"] == "SUBINDUSTRY"


def test_build_simulation_payload_rejects_empty_expression():
    with pytest.raises(BrainPayloadException):
        build_simulation_payload("   ")


def test_build_simulation_payload_rejects_invalid_universe():
    with pytest.raises(BrainPayloadException):
        build_simulation_payload("rank(close)", {"universe": "INVALID_UNIVERSE_XYZ"})


def test_build_simulation_payload_rejects_invalid_neutralization():
    with pytest.raises(BrainPayloadException):
        build_simulation_payload("rank(close)", {"neutralization": "INVALID_NEUT"})
