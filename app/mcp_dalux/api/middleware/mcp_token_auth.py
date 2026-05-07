from __future__ import annotations

import logging
import secrets

from mcp_dalux.config import Config
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.status import HTTP_401_UNAUTHORIZED

logger = logging.getLogger(__name__)


class MCPTokenAuthMiddleware(BaseHTTPMiddleware):
    """Require Bearer token or X-API-KEY."""

    async def dispatch(self, request: Request, call_next):
        token = Config.MCP_API_TOKEN

        # No auth configured allows all
        if not token:
            return await call_next(request)

        # Health endpoint bypass
        if request.url.path.rstrip("/") == "/health":
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        api_key = request.headers.get("x-api-key", "")

        valid = False

        # Authorization: Bearer <token>
        if auth_header:
            parts = auth_header.split(" ", 1)

            if len(parts) == 2 and parts[0].lower() == "bearer" and secrets.compare_digest(parts[1], token):
                valid = True

        # X-API-KEY: <token>
        if api_key and secrets.compare_digest(api_key, token):
            valid = True

        if not valid:
            logger.warning(
                "MCP auth failed from=%s path=%s",
                request.client.host if request.client else "unknown",
                request.url.path,
            )

            return PlainTextResponse(
                "Unauthorized",
                status_code=HTTP_401_UNAUTHORIZED,
            )

        return await call_next(request)
