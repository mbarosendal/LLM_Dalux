import sys
import logging
from mcp_dalux.config import Config
from mcp_dalux.orchestration import mcp
from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
import json

logger = logging.getLogger(__name__)

def main() -> None:

    try:
        Config.validate()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    logger.info("Starting MCP server for Dalux via stdio.")

    mcp.run(transport="stdio", show_banner=False)

if __name__ == "__main__":
    main()