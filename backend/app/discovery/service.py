from datetime import datetime, timezone

from app.discovery.connectors import DiscoveryConnector, DiscoveryObservationData


class DiscoveryService:
    """Orchestrates connectors without allowing connectors to mutate Asset state."""

    def collect(self, connector: DiscoveryConnector) -> list[DiscoveryObservationData]:
        return connector.discover()

    @staticmethod
    def normalize_observation(observation: DiscoveryObservationData) -> dict:
        data = dict(observation.fields)
        data["source"] = observation.source
        data["observed_at"] = observation.observed_at.astimezone(timezone.utc)
        return data

    @staticmethod
    def summarize(observations: list[DiscoveryObservationData]) -> dict[str, int]:
        return {
            "total_observations": len(observations),
            "with_agent_id": sum(bool(x.fields.get("AGENT_ID") or x.fields.get("agent_id")) for x in observations),
            "with_serial": sum(bool(x.fields.get("SERIAL_NUMBER") or x.fields.get("serial_number")) for x in observations),
        }
