from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text

from config import Settings, get_settings
from database.connection import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def root_health() -> dict:
    return {"status": "ok", "service": "beingai-api"}


@router.get("/api/health")
async def api_health(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "service": "beingai-api",
        "environment": settings.app_env,
    }


@router.get("/api/ready")
async def api_ready(
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    checks: dict[str, str] = {
        "api": "ok",
        "environment": settings.app_env,
        "auth": "enabled" if settings.auth_enabled else "demo_fallback",
        "n8n": "live" if settings.n8n_enabled else "mock",
        "openai": "configured" if settings.openai_api_key else "fallback_planner",
    }

    if not settings.database_configured:
        checks["database"] = "missing_database_url"
    elif engine is None:
        checks["database"] = "unavailable"
    else:
        try:
            with engine.connect() as connection:
                connection.execute(text("select 1"))
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "unavailable"

    blocking = [name for name, state in checks.items() if state in {"unavailable", "missing_database_url"}]
    status_code = 503 if blocking else 200

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if status_code == 200 else "degraded",
            "checks": checks,
        },
    )
