
from mcp_dalux.language_model.clients.base_client import BaseClient

class ClaudeClient(BaseClient):

    @property
    def model_name(self) -> str:
        return "Claude"
    
    @property
    def version(self) -> str:
        return "Unknown"

    async def generate_text(self, text: str, instructions: str, tools: list | None = None) -> str:
        tools_description = ", ".join(tools) if tools else "no tools"
        return (
            f"Claude generated text for: {text} "
            f"with instructions: {instructions} and tools: {tools_description}"
        )