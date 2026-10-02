from app.discovery.identity import resolve_identity


def test_agent_id_has_highest_identity_confidence() -> None:
    status, asset_id, confidence = resolve_identity(
        {"AGENT_ID": "A-01", "HOSTNAME": "pc01"},
        [
            {"identifier_type": "HOSTNAME", "identifier_value": "pc01", "asset_id": 9},
            {"identifier_type": "AGENT_ID", "identifier_value": "A-01", "asset_id": 3},
        ],
    )
    assert (status, asset_id, confidence) == ("MATCHED", 3, 100)


def test_unknown_observation_is_new() -> None:
    assert resolve_identity({"SERIAL_NUMBER": "new"}, []) == ("NEW", None, 0)


def test_equal_confidence_is_ambiguous() -> None:
    status, asset_id, confidence = resolve_identity(
        {"SERIAL_NUMBER": "same"},
        [
            {"identifier_type": "SERIAL_NUMBER", "identifier_value": "same", "asset_id": 1},
            {"identifier_type": "SERIAL_NUMBER", "identifier_value": "same", "asset_id": 2},
        ],
    )
    assert (status, asset_id, confidence) == ("AMBIGUOUS", None, 90)