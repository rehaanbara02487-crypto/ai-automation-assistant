from typing import Any

from fastapi import Depends, HTTPException, Request

from auth.clerk_jwt import verify_clerk_token
from config import Settings, get_settings
from database.store import AutomationStore


def get_store(settings: Settings = Depends(get_settings)) -> AutomationStore:
    if not hasattr(get_store, "_store"):
        get_store._store = AutomationStore(settings)  # type: ignore[attr-defined]
    return get_store._store  # type: ignore[attr-defined]


def _email_from_claims(claims: dict[str, Any]) -> str | None:
    email = claims.get("email")
    if isinstance(email, str) and email:
        return email

    primary = claims.get("primary_email_address")
    if isinstance(primary, str) and primary:
        return primary

    return None


async def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
) -> str:
    if not settings.auth_enabled:
        await store.ensure_user(settings.mock_user_id, email="demo@local")
        return settings.mock_user_id

    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    claims = verify_clerk_token(token, settings.clerk_jwt_issuer)
    user_id = claims.get("sub")
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=401, detail="Invalid token subject")

    await store.ensure_user(
        user_id,
        email=_email_from_claims(claims),
        full_name=claims.get("name") if isinstance(claims.get("name"), str) else None,
    )
    return user_id
