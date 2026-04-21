from abc import ABC, abstractmethod

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
    async def generate_context(self, prompt: str, instructions: str, tools: list | None = None) -> str:
        """Generate context for the language model from a prompt and instructions."""
        pass