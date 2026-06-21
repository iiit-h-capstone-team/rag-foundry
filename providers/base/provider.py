from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        model: str,
        messages: list,
        **kwargs
    ):
        """
        Generate a response from the model.
        """
        pass

    @abstractmethod
    def health(self) -> dict:
        """
        Provider diagnostics.
        """
        pass