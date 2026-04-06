import sys
import logging
from config import Config
from orchestration import mcp

logger = logging.getLogger(__name__)

def main() -> None:

    print("Starting MCP server for Dalux via stdio.")

    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}")
        sys.exit(1)

    logger.info("Starting MCP server for Dalux via stdio.")

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()