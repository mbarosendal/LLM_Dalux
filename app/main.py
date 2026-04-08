import sys
import logging
from pathlib import Path

if __package__ in (None, ""):
    # Support direct script execution (python app/main.py) by adding project root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Config
from app.orchestration import mcp
from app.adapters.dalux_adapter import DaluxAdapter
import json

logger = logging.getLogger(__name__)

def main() -> None:
    try:
        Config.validate()

        # adapter = DaluxAdapter()
        # tasks = adapter.get_tasks(Config.DALUX_PROJECT_ID) # test
        # tasks = adapter.get_task(Config.DALUX_PROJECT_ID, "S432130555081916416") # test
        # tasks = adapter.get_task_attachments(Config.DALUX_PROJECT_ID) # test
        # tasks = adapter.get_task_changes(Config.DALUX_PROJECT_ID) # test

        # with open("full.json", "w", encoding="utf-8") as f:
        #     json.dump(tasks, f, indent=2, ensure_ascii=False)
        # print("Saved full response to full.json")

        # print(json.dumps(tasks, indent=2, ensure_ascii=False)) #test
        # return
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    logger.info("Starting MCP server for Dalux via stdio.")

    mcp.run(transport="stdio", show_banner=False)

if __name__ == "__main__":
    main()