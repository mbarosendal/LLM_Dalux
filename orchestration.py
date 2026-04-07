import logging
from fastmcp import FastMCP
from language_model.prompts.system_prompt import SYSTEM_PROMPT

# Set up MCP object with resources
mcp = FastMCP(
    name="dalux-mcp",
    instructions=SYSTEM_PROMPT,
)

