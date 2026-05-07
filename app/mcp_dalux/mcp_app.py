from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse

from mcp_dalux.api.middleware.mcp_token_auth import MCPTokenAuthMiddleware
from mcp_dalux.api.middleware.request_logging import RequestLoggingMiddleware
from mcp_dalux.config import Config
from mcp_dalux.mcp_setup import create_mcp_server


async def health(request):
    return PlainTextResponse("ok")


def create_mcp_asgi_app():
    mcp = create_mcp_server()

    app = mcp.http_app(
        path="/mcp",
        transport=Config.MCP_TRANSPORT,
        middleware=[
            Middleware(RequestLoggingMiddleware),
            Middleware(MCPTokenAuthMiddleware),
        ],
    )

    app.add_route("/health", health, methods=["GET"])

    return app
