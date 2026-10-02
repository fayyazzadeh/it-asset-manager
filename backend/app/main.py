from fastapi import FastAPI

from app.api.assets import router as assets_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.2.0")
app.include_router(assets_router, prefix="/api")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}