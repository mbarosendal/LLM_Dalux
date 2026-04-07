import sys
import logging
from config import Config
from orchestration import mcp
import json

from adapters.dalux_adapter import DaluxAdapter # test

logger = logging.getLogger(__name__)

def main() -> None:

    print("Starting MCP server for Dalux via stdio.")

    try:
        Config.validate()

        adapter = DaluxAdapter()
        # tasks = adapter.get_tasks(Config.DALUX_PROJECT_ID) # test
        # tasks = adapter.get_task(Config.DALUX_PROJECT_ID, "S432130555081916416") # test
        # tasks = adapter.get_task_attachments(Config.DALUX_PROJECT_ID) # test
        tasks = adapter.get_task_changes(Config.DALUX_PROJECT_ID) # test

        # with open("full.json", "w", encoding="utf-8") as f:
        #     json.dump(tasks, f, indent=2, ensure_ascii=False)
        # print("Saved full response to full.json")

        print(json.dumps(tasks, indent=2, ensure_ascii=False)) #test

        return
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}")
        sys.exit(1)

    logger.info("Starting MCP server for Dalux via stdio.")



    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()