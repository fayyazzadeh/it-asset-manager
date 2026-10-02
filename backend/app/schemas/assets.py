from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    asset_tag: str
    asset_type_id: int
    asset_subtype_id: int | None = None
    network_id: int | None = None
    location_id: int | None = None
    status: str = "DISCOVERED"
    computer_name: str | None = None
    hostname: str | None = None
    fqdn: str | None = None
    domain: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    description: str | None = None


class AssetRead(AssetCreate):
    id: int
    first_seen: datetime | None
    last_seen: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)