from functools import lru_cache

import jwt
from fastapi import HTTPException
from jwt import PyJWKClient


@lru_cache
def _jwks_client(issuer: str) -> PyJWKClient:
    normalized = issuer.rstrip("/")
    return PyJWKClient(f"{normalized}/.well-known/jwks.json")


def verify_clerk_token(token: str, issuer: str) -> dict:
    try:
        client = _jwks_client(issuer)
        signing_key = client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer.rstrip("/"),
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
