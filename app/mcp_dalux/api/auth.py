from __future__ import annotations

from fastapi import Header, HTTPException, status

# Start with one hardcoded token.
# Later this can be replaced by a real auth provider or project-scoped auth.

EXPECTED_TOKEN = "temporary-token-4321"

def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Very small auth gate for the first online version.

    Expected header:
    Authorization: Bearer <token>
    """

    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != EXPECTED_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
