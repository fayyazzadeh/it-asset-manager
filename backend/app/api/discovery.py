from fastapi import APIRouter, Depends

from app.core.security import require_roles
from app.discovery.connectors import ManualConnector
from app.discovery.service import DiscoveryService
from app.models import User
from app.schemas.discovery import ManualDiscoveryRequest

router = APIRouter(prefix="/discovery", tags=["discovery"])
service = DiscoveryService()


@router.post("/preview")
def preview_discovery(
    payload: ManualDiscoveryRequest,
    _user: User = Depends(require_roles("ADMIN", "OPERATOR")),
) -> dict:
    observations = service.collect(ManualConnector(payload.fields))
    return {
        "source": "MANUAL",
        "observations": [service.normalize_observation(item) for item in observations],
        "summary": service.summarize(observations),
    }
