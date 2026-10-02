from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password, hash_refresh_token, verify_password
from app.db import get_db
from app.models import RefreshToken, Role, User, UserRole
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def issue_tokens(user: User, roles: list[str], db: Session) -> TokenResponse:
    access = create_access_token(user.id, roles)
    raw_refresh, refresh_hash = create_refresh_token()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        created_at=datetime.now(timezone.utc),
    ))
    db.commit()
    return TokenResponse(access_token=access, refresh_token=raw_refresh)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(status_code=409, detail="username already exists")
    if db.scalar(select(User).where(User.email == str(payload.email))):
        raise HTTPException(status_code=409, detail="email already exists")
    user = User(
        username=payload.username,
        email=str(payload.email),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    role = db.scalar(select(Role).where(Role.code == "ADMIN" if db.scalar(select(User).where(User.id != user.id)) is None else "OPERATOR"))
    if role is None:
        role = Role(code="ADMIN", name="Administrator")
        db.add(role)
        db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    return issue_tokens(user, [role.code], db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    roles = list(db.scalars(select(Role.code).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)))
    return issue_tokens(user, roles, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_hash = hash_refresh_token(payload.refresh_token)
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    now = datetime.now(timezone.utc)
    if stored is None or stored.revoked_at is not None or stored.expires_at <= now:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    stored.revoked_at = now
    user = db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="inactive user")
    roles = list(db.scalars(select(Role.code).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)))
    return issue_tokens(user, roles, db)
