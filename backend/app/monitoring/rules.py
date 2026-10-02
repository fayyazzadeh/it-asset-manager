from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class Rule:
    operator: str
    threshold: float


def matches(rule: Rule, value: float) -> bool:
    return {
        ">": value > rule.threshold,
        ">=": value >= rule.threshold,
        "<": value < rule.threshold,
        "<=": value <= rule.threshold,
        "==": value == rule.threshold,
        "!=": value != rule.threshold,
    }.get(rule.operator, False)


def fingerprint(asset_id: int, alert_rule_id: int, metric_code: str, resource_identifier: str | None = None) -> str:
    raw = f"{asset_id}:{alert_rule_id}:{metric_code}:{resource_identifier or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()
