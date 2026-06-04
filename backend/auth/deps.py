from typing import Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth.clerk_jwt import verify_clerk_token
from config import Settings, get_settings
from database.session import get_db_session
from database.store import AutomationStore


def get_store(db: Session = Depends(get_db_session)) -> AutomationStore:
    return AutomationStore(db)


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
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured. Set CLERK_SECRET_KEY and CLERK_JWT_ISSUER.",
        )

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
