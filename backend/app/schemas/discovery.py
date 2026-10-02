from typing import Any

from pydantic import BaseModel, Field


class ManualDiscoveryRequest(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)


class EnrollmentTokenCreate(BaseModel):
    asset_id: int
    expires_in_hours: int = Field(default=24, ge=1, le=168)


class EnrollmentTokenResponse(BaseModel):
    token: str
    expires_at: str | None


class AgentEnrollRequest(BaseModel):
    agent_id: str = Field(min_length=8, max_length=255)
    version: str | None = Field(default=None, max_length=50)
    os: str | None = Field(default=None, max_length=150)
    ip_address: str | None = None


class AgentEnrollResponse(BaseModel):
    agent_id: str
    credential: str
    asset_id: int


class AgentHeartbeatRequest(BaseModel):
    version: str | None = Field(default=None, max_length=50)
    ip_address: str | None = None
