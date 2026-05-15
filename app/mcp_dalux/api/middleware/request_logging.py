from __future__ import annotations

import logging
import time
import uuid
from typing import Awaitable, Callable

from mcp_dalux.config import Config
from mcp_dalux.logging_setup import append_structured_log_event, get_file_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)
request_logger = get_file_logger("mcp_dalux.request", "incoming_request.log")


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


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming HTTP requests with request_id, latency, and redacted headers."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.monotonic()
        client_host = request.client.host if request.client else "unknown"
        path = _redact_path(request.url.path)

        # Log incoming request (redact Authorization header)
        headers_display = dict(request.headers)
        if "authorization" in headers_display:
            headers_display["authorization"] = "[REDACTED]"
        if "x-api-key" in headers_display:
            headers_display["x-api-key"] = "[REDACTED]"

        request_logger.info(f"request_id={request_id} | {request.method} {path} | client={client_host}")
        append_structured_log_event(
            log_filename="incoming_request.log",
            source="request_middleware",
            event="request_started",
            payload={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "client": client_host,
                "headers": headers_display,
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            latency_ms = (time.monotonic() - start_time) * 1000
            request_logger.error(f"request_id={request_id} | {request.method} {path} | error={exc.__class__.__name__} | latency={latency_ms:.2f}ms")
            append_structured_log_event(
                log_filename="incoming_request.log",
                source="request_middleware",
                event="request_failed",
                payload={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "client": client_host,
                    "error": exc.__class__.__name__,
                    "latency_ms": round(latency_ms, 2),
                },
            )
            raise

        latency_ms = (time.monotonic() - start_time) * 1000
        request_logger.info(f"request_id={request_id} | {request.method} {path} | status={response.status_code} | latency={latency_ms:.2f}ms")
        append_structured_log_event(
            log_filename="incoming_request.log",
            source="request_middleware",
            event="request_finished",
            payload={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "client": client_host,
                "status_code": response.status_code,
                "latency_ms": round(latency_ms, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
