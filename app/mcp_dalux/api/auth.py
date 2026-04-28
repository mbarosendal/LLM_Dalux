from __future__ import annotations

from hmac import compare_digest

from fastapi import Header, HTTPException, status

from mcp_dalux.config import Config


def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Bearer-token authentication for API endpoints.

    Expected header:
    Authorization: Bearer <token>
    """

    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise auth_error

    # Split the header into scheme and token.
    scheme, _, token = authorization.partition(" ")
    configured_token = Config.API_AUTH_TOKEN

    if scheme.lower() != "bearer" or not token or not configured_token:
        raise auth_error

    # Use compare_digest for constant-time comparison to mitigate timing attacks.
    if not compare_digest(token, configured_token):
        raise auth_error
