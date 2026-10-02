from datetime import datetime, timezone

from ping3 import ping


def choose_ping_target(asset, interfaces: list) -> str | None:
    for interface in interfaces:
        if getattr(interface, "ip_address", None):
            return interface.ip_address
    for field in ("fqdn", "hostname", "computer_name"):
        value = getattr(asset, field, None)
        if value:
            return value
    return None


def collect_icmp(target: str, timeout_seconds: int = 3) -> float | None:
    if not target:
        return None
    result = ping(target, timeout=timeout_seconds, unit="ms")
    if result is None or result is False:
        return None
    return float(result)


def heartbeat_age_seconds(last_seen: datetime | None, now: datetime | None = None) -> float | None:
    if last_seen is None:
        return None
    current = now or datetime.now(timezone.utc)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    return max(0.0, (current - last_seen).total_seconds())
