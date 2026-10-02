from typing import Any

from pydantic import BaseModel, Field


class ManualDiscoveryRequest(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)
