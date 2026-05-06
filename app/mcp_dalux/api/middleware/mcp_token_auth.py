from __future__ import annotations

import logging

from mcp_dalux.config import Config
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_401_UNAUTHORIZED

logger = logging.getLogger(__name__)


class MCPTokenAuthMiddleware(BaseHTTPMiddleware):
    """Require a bearer token or X-API-KEY header"""

    async def dispatch(self, request: Request, call_next):
        token = Config.MCP_API_TOKEN
        # # No token configured -> allow all
        if not token:
            return await call_next(request)

        # Allow health probes to skip auth if they hit /health
        if request.url.path.rstrip("/") == "/health":
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        api_key = request.headers.get("x-api-key")

        valid = False
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == token:
                valid = True
        if api_key and api_key == token:
            valid = True

        if not valid:
            logger.warning("MCP token auth failed from %s path=%s", request.client.host if request.client else "unknown", request.url.path)
            return Response(status_code=HTTP_401_UNAUTHORIZED, content="Unauthorized")

        return await call_next(request)
