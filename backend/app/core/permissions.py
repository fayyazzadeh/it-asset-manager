from dataclasses import dataclass
from typing import Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models import Role, User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    user_id: int
    username: str
    roles: frozenset[str]


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedPrincipal:
    unauthorized = HTTPException(
        status_code=401,
        detail="valid bearer token required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "type"]},
        )
        if claims.get("type") != "access":
            raise unauthorized
        user_id = int(claims["sub"])
    except (jwt.PyJWTError, TypeError, ValueError):
        raise unauthorized from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    # Resolve roles from the database on every request so revocation takes
    # effect immediately instead of trusting potentially stale token claims.
    roles = frozenset(
        db.scalars(
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
        )
    )
    if not roles:
        raise HTTPException(status_code=403, detail="user has no assigned role")

    return AuthenticatedPrincipal(user_id=user.id, username=user.username, roles=roles)


def require_roles(*allowed_roles: str) -> Callable:
    normalized = frozenset(role.upper() for role in allowed_roles)

    def role_guard(
        principal: AuthenticatedPrincipal = Depends(get_current_principal),
    ) -> AuthenticatedPrincipal:
        if principal.roles.isdisjoint(normalized):
            raise HTTPException(status_code=403, detail="insufficient role")
        return principal

    return role_guard
