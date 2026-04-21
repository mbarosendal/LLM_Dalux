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
    async def generate_text(self, text: str, instructions: str, tools: list | None = None) -> str:
        """Generate text for the language model from a text and instructions."""
        pass