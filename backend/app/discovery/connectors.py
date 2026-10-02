from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class DiscoveryObservationData:
    source: str
    observed_at: datetime
    fields: dict[str, str | int | float | bool | None]
    raw_data: dict | None = None


class DiscoveryConnector(Protocol):
    name: str

    def discover(self) -> list[DiscoveryObservationData]:
        ...


class ManualConnector:
    name = "MANUAL"

    def __init__(self, fields: dict[str, str | int | float | bool | None]):
        self.fields = fields

    def discover(self) -> list[DiscoveryObservationData]:
        return [DiscoveryObservationData(
            source=self.name,
            observed_at=datetime.now(timezone.utc),
            fields=self.fields,
            raw_data=self.fields,
        )]
