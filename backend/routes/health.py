from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from config import Settings, get_settings
from database.store import AutomationStore
from auth.deps import get_store

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
    store: AutomationStore = Depends(get_store),
) -> JSONResponse:
    checks: dict[str, str] = {
        "api": "ok",
        "environment": settings.app_env,
        "auth": "enabled" if settings.auth_enabled else "demo_fallback",
        "n8n": "live" if settings.n8n_enabled else "mock",
        "openai": "configured" if settings.openai_api_key else "fallback_planner",
    }

    if settings.supabase_configured:
        try:
            store.client.table("plans").select("id").limit(1).execute()  # type: ignore[union-attr]
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "unavailable"
    else:
        checks["database"] = "memory_fallback"

    blocking = [name for name, state in checks.items() if state == "unavailable"]
    status_code = 503 if blocking else 200

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if status_code == 200 else "degraded",
            "checks": checks,
        },
    )
