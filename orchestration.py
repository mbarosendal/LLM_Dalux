from fastmcp import FastMCP
from language_model.prompts.system_prompt import SYSTEM_PROMPT
from adapters.dalux_adapter import DaluxAdapter
from tools.dalux_tools import register_dalux_tools

# Set up MCP object with resources
mcp = FastMCP(
    name="dalux-mcp",
    instructions=SYSTEM_PROMPT,
)

# Shared adapter instance
_adapter = DaluxAdapter()
register_dalux_tools(mcp, _adapter)

# if __name__ == "__main__":
#     print(get_tasks())