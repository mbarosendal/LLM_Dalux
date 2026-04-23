from __future__ import annotations

from fastapi import FastAPI

from mcp_dalux.api.routes_health import router as health_router
from mcp_dalux.api.routes_sessions import router as sessions_router


def create_http_app() -> FastAPI:
    app = FastAPI(
		title="Dalux HTTP API",
		version="0.1.0",
		description="HTTP entrypoint for the online Dalux integration.",
	)

# Register routers here once they exist. Keep this file focused on assembling the API application.

# Build order:
# 1. Keep this file small. It should only assemble the API application.
# 2. Register routers here once they exist.
# 3. Put auth, schemas, session state, and agent logic in separate modules.
# 4. Later, mount the same services behind other transports if needed.
#
# For the first iteration, aim for these endpoints:
# - GET /health
# - POST /sessions/create
# - POST /sessions/{sessionId}/prompts/send
#
# The HTTP layer should not know how prompts are processed internally;
# it should just validate input, call a service, and return structured output.

    app.include_router(health_router)
    app.include_router(sessions_router)
    return app


app = create_http_app()
