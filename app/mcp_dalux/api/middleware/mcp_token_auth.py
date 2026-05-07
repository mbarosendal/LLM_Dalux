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
    """Require auth for MCP requests.

    Modes:
    - bearer: Authorization Bearer token or X-API-KEY header
    - url-token: /mcp/<token>[/...]
    - none: disabled
    """

    @staticmethod
    def _redact_path(path: str) -> str:
        if Config.MCP_AUTH_MODE != "url-token":
            return path

        base = Config.MCP_HTTP_PATH.rstrip("/") or "/"
        prefix = f"{base}/"

        if not path.startswith(prefix):
            return path

        remainder = path[len(prefix) :]
        if not remainder:
            return path

        slash_idx = remainder.find("/")
        if slash_idx == -1:
            return f"{base}/[REDACTED]"

        return f"{base}/[REDACTED]{remainder[slash_idx:]}"

    @staticmethod
    def _validate_url_token_path(path: str, token: str) -> tuple[bool, str | None]:
        base = Config.MCP_HTTP_PATH.rstrip("/") or "/"
        prefix = f"{base}/"

        if not path.startswith(prefix):
            return False, None

        remainder = path[len(prefix) :]
        if not remainder:
            return False, None

        slash_idx = remainder.find("/")
        provided_token = remainder if slash_idx == -1 else remainder[:slash_idx]

        if not provided_token or not secrets.compare_digest(provided_token, token):
            return False, None

        suffix = "" if slash_idx == -1 else remainder[slash_idx:]
        return True, f"{base}{suffix}"

    async def dispatch(self, request: Request, call_next):
        mode = Config.MCP_AUTH_MODE
        token = Config.MCP_API_TOKEN

        if mode == "none":
            return await call_next(request)

        # No auth configured allows all
        if not token:
            return await call_next(request)

        # Health endpoint bypass
        if request.url.path.rstrip("/") == "/health":
            return await call_next(request)

        if mode == "url-token":
            valid, rewritten_path = self._validate_url_token_path(request.url.path, token)

            if not valid:
                logger.warning(
                    "MCP auth failed from=%s path=%s",
                    request.client.host if request.client else "unknown",
                    self._redact_path(request.url.path),
                )

                return PlainTextResponse(
                    "Unauthorized",
                    status_code=HTTP_401_UNAUTHORIZED,
                )

            # Hide token segment from downstream routing and logs.
            request.scope["path"] = rewritten_path
            request.scope["raw_path"] = rewritten_path.encode("utf-8")
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
                self._redact_path(request.url.path),
            )

            return PlainTextResponse(
                "Unauthorized",
                status_code=HTTP_401_UNAUTHORIZED,
            )

        return await call_next(request)
