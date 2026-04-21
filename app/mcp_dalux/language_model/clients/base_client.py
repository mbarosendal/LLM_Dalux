from abc import ABC, abstractmethod

from mcp_dalux.language_model.contracts import AgentDecision

class BaseClient(ABC):

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the language model."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the language model."""
        pass

    @abstractmethod
    async def generate_decision(self, text: str, instructions: str, tools: list[str] | None = None) -> AgentDecision:
        """Return the model's next decision for a prompt turn."""
        pass