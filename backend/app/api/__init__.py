from app.api.assets import router as assets_router
from app.api.auth import router as auth_router
from app.api.discovery import router as discovery_router

__all__ = ["assets_router", "auth_router", "discovery_router"]
