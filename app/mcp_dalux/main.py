import logging
import sys

import uvicorn

from mcp_dalux.api.app import create_http_app
from mcp_dalux.config import Config
from mcp_dalux.logging_setup import configure_logging
from mcp_dalux.mcp_setup import create_mcp_server

logger = logging.getLogger(__name__)

configure_logging()


def main() -> None:
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    if Config.APP_MODE == "web_api":
        logger.info("Starting Dalux web API.")
        app = create_http_app()
        uvicorn.run(
            app,
            host=Config.HOST,
            port=Config.PORT,
            reload=False,
        )
        return

    if Config.APP_MODE == "mcp":
        logger.info(f"Starting MCP server via {Config.MCP_TRANSPORT}.")
        run_kwargs = {
            "transport": Config.MCP_TRANSPORT,
            "show_banner": False,
        }
        if Config.MCP_TRANSPORT != "stdio":
            run_kwargs.update(
                {
                    "host": Config.MCP_HOST,
                    "port": Config.MCP_PORT,
                }
            )
        create_mcp_server().run(**run_kwargs)
        return

    raise ValueError(f"Unsupported APP_MODE: {Config.APP_MODE}")


if __name__ == "__main__":
    main()
