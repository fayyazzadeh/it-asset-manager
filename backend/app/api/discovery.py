from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_refresh_token, require_roles
from app.db import get_db
from app.discovery.connectors import ManualConnector
from app.discovery.service import DiscoveryService
from app.models import Agent, AgentToken, Asset, EnrollmentToken, User
from app.schemas.discovery import (
    AgentEnrollRequest,
    AgentEnrollResponse,
    AgentHeartbeatRequest,
    EnrollmentTokenCreate,
    EnrollmentTokenResponse,
    ManualDiscoveryRequest,
)

router = APIRouter(prefix="/discovery", tags=["discovery"])
service = DiscoveryService()
agent_bearer = HTTPBearer(auto_error=False)


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


@router.post("/enrollment-tokens", response_model=EnrollmentTokenResponse, status_code=201)
def create_enrollment_token(
    payload: EnrollmentTokenCreate,
    user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
) -> EnrollmentTokenResponse:
    if db.get(Asset, payload.asset_id) is None:
        raise HTTPException(status_code=404, detail="asset not found")
    raw = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    db.add(EnrollmentToken(
        asset_id=payload.asset_id,
        token_hash=hash_refresh_token(raw),
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        created_by=user.id,
    ))
    db.commit()
    return EnrollmentTokenResponse(token=raw, expires_at=expires_at.isoformat())


def _get_agent_from_token(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> Agent:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="agent credential required")
    token_hash = hash_refresh_token(credentials.credentials)
    row = db.execute(
        select(AgentToken, Agent)
        .join(Agent, Agent.id == AgentToken.agent_id)
        .where(
            AgentToken.token_hash == token_hash,
            AgentToken.revoked_at.is_(None),
            (AgentToken.expires_at.is_(None) | (AgentToken.expires_at > datetime.now(timezone.utc))),
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid agent credential")
    return row[1]


@router.post("/agents/enroll", response_model=AgentEnrollResponse)
def enroll_agent(payload: AgentEnrollRequest, db: Session = Depends(get_db)) -> AgentEnrollResponse:
    enrollment = db.scalar(
        select(EnrollmentToken).where(
            EnrollmentToken.token_hash == hash_refresh_token(payload.enrollment_token),
            EnrollmentToken.used_at.is_(None),
            (EnrollmentToken.expires_at.is_(None) | (EnrollmentToken.expires_at > datetime.now(timezone.utc))),
        )
    )
    if enrollment is None:
        raise HTTPException(status_code=401, detail="invalid enrollment token")
    if db.scalar(select(Agent).where(Agent.agent_id == payload.agent_id)):
        raise HTTPException(status_code=409, detail="agent_id already enrolled")

    now = datetime.now(timezone.utc)
    agent = Agent(
        asset_id=enrollment.asset_id,
        agent_id=payload.agent_id,
        version=payload.version,
        status="ACTIVE",
        last_seen=now,
        ip_address=payload.ip_address,
        os=payload.os,
        installed_at=now,
    )
    db.add(agent)
    db.flush()

    credential = secrets.token_urlsafe(48)
    db.add(AgentToken(
        agent_id=agent.id,
        token_hash=hash_refresh_token(credential),
        expires_at=now + timedelta(days=30),
        created_at=now,
    ))
    enrollment.used_at = now
    db.commit()
    return AgentEnrollResponse(
        agent_id=agent.agent_id,
        credential=credential,
        asset_id=agent.asset_id,
    )


@router.post("/agents/heartbeat")
def agent_heartbeat(
    payload: AgentHeartbeatRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(agent_bearer),
    db: Session = Depends(get_db),
) -> dict:
    agent = _get_agent_from_token(credentials, db)
    now = datetime.now(timezone.utc)
    agent.last_seen = now
    if payload.version:
        agent.version = payload.version
    if payload.ip_address:
        agent.ip_address = payload.ip_address
    db.commit()
    return {"status": "ok", "agent_id": agent.agent_id, "last_seen": now.isoformat()}
