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