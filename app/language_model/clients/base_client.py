from abc import ABC, abstractmethod

class baseClient(ABC):

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
    def send_message(self, message: str) -> str:
        """Send a message to the language model and get a response."""
        pass

    @abstractmethod
    def send_message_with_tools(self, message: str, tools: list) -> str:
        """Send a message along with available tools to the language model and get a response."""
        pass