from fastapi import APIRouter

from app.discovery.connectors import ManualConnector
from app.discovery.service import DiscoveryService
from app.schemas.discovery import ManualDiscoveryRequest

router = APIRouter(prefix="/discovery", tags=["discovery"])
service = DiscoveryService()


@router.post("/preview")
def preview_discovery(payload: ManualDiscoveryRequest) -> dict:
    observations = service.collect(ManualConnector(payload.fields))
    return {
        "source": "MANUAL",
        "observations": [service.normalize_observation(item) for item in observations],
        "summary": service.summarize(observations),
    }
