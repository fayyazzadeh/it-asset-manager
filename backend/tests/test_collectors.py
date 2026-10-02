from datetime import datetime, timezone

from app.monitoring.collectors import choose_ping_target, heartbeat_age_seconds


class AssetStub:
    fqdn = "server.example.local"
    hostname = "server"
    computer_name = "SERVER"


class InterfaceStub:
    def __init__(self, ip_address):
        self.ip_address = ip_address


def test_choose_ping_target_prefers_interface_ip():
    assert choose_ping_target(AssetStub(), [InterfaceStub("172.20.20.10")]) == "172.20.20.10"


def test_choose_ping_target_falls_back_to_hostname():
    assert choose_ping_target(AssetStub(), []) == "server.example.local"


def test_heartbeat_age_is_non_negative():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    seen = datetime(2025, 12, 31, 23, 59, 30, tzinfo=timezone.utc)
    assert heartbeat_age_seconds(seen, now) == 30.0
