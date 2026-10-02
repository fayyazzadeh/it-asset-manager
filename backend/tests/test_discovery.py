from datetime import datetime, timezone

from app.discovery.connectors import ManualConnector
from app.discovery.service import DiscoveryService


def test_manual_connector_returns_observation() -> None:
    connector = ManualConnector({"AGENT_ID": "agent-1", "SERIAL_NUMBER": "SN-1"})
    observations = DiscoveryService().collect(connector)
    assert len(observations) == 1
    assert observations[0].source == "MANUAL"
    assert observations[0].fields["AGENT_ID"] == "agent-1"


def test_summary_counts_identity_fields() -> None:
    connector = ManualConnector({"AGENT_ID": "agent-1", "SERIAL_NUMBER": "SN-1"})
    observations = connector.discover()
    assert DiscoveryService.summarize(observations) == {
        "total_observations": 1,
        "with_agent_id": 1,
        "with_serial": 1,
    }


def test_normalization_uses_utc() -> None:
    observation = ManualConnector({"HOSTNAME": "pc01"}).discover()[0]
    normalized = DiscoveryService.normalize_observation(observation)
    assert normalized["source"] == "MANUAL"
    assert normalized["observed_at"].tzinfo == timezone.utc
