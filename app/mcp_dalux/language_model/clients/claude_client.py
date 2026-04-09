
from mcp_dalux.language_model.clients.base_client import BaseClient

class ClaudeClient(BaseClient):

    @property
    def model_name(self) -> str:
        return "Claude"
    
    @property
    def version(self) -> str:
        return "Unknown"