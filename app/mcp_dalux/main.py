import logging
import sys

import uvicorn

from mcp_dalux.api.app import create_http_app
from mcp_dalux.config import Config
from mcp_dalux.logging_setup import configure_logging
from mcp_dalux.orchestration import create_mcp_server

logger = logging.getLogger(__name__)

configure_logging()


def main() -> None:

    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    if Config.MCP_TRANSPORT == "stdio":
        logger.info("Starting MCP server for Dalux via stdio.")
        mcp = create_mcp_server()
        mcp.run(transport="stdio", show_banner=False)
        return

    if Config.MCP_TRANSPORT == "http":
        logger.info("Starting MCP server for Dalux via HTTP.")
        app = create_http_app()
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            reload=False,
        )
        return

    raise ValueError(f"Unsupported MCP_TRANSPORT: {Config.MCP_TRANSPORT}")


if __name__ == "__main__":
    main()
