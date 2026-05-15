from abc import ABC, abstractmethod

from mcp_dalux.llm.contracts import AgentDecision, LLMError


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
        """Return the model's next decision for a prompt turn.

        Raises LLMError if the request fails.
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the LLM client is healthy and can connect to the service."""
        pass
