from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from mcp_dalux.api.auth import require_api_token
from mcp_dalux.api.middleware.request_logging import RequestLoggingMiddleware
from mcp_dalux.api.routes_health import router as health_router
from mcp_dalux.api.routes_sessions import router as sessions_router
from mcp_dalux.config import Config
from mcp_dalux.logging_setup import configure_logging

configure_logging()


def create_http_app() -> FastAPI:
    app = FastAPI(
        title="Dalux HTTP API",
        version="0.1.0",
        description="HTTP entrypoint for the online integration.",
    )

    # Request logging middleware wraps all traffic (run outermost).
    app.add_middleware(RequestLoggingMiddleware)

    # Reject requests with unexpected Host headers to reduce host header attack surface.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=Config.TRUSTED_HOSTS)

    # CORS is only needed for browser-based callers. Keep disabled unless origins are explicitly configured.
    if Config.CORS_ALLOW_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=Config.CORS_ALLOW_ORIGINS,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.include_router(health_router)
    app.include_router(sessions_router, dependencies=[Depends(require_api_token)])
    return app


app = create_http_app()
