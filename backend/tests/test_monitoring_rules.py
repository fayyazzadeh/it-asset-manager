from app.monitoring.rules import Rule, fingerprint, matches


def test_threshold_operators() -> None:
    assert matches(Rule(">", 80), 81)
    assert matches(Rule(">=", 80), 80)
    assert matches(Rule("<", 20), 19)
    assert matches(Rule("<=", 20), 20)
    assert matches(Rule("==", 10), 10)
    assert matches(Rule("!=", 10), 11)


def test_fingerprint_is_deterministic() -> None:
    assert fingerprint(1, 2, "cpu_usage", "total") == fingerprint(1, 2, "cpu_usage", "total")
    assert fingerprint(1, 2, "cpu_usage", "total") != fingerprint(1, 2, "cpu_usage", "core0")