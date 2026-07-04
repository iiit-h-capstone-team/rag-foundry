"""Base provider strategy class."""

from abc import abstractmethod
from core.strategy import BaseStrategy


class ProviderStrategy(BaseStrategy):
    """Base class for LLM provider strategies."""

    @abstractmethod
    def generate(self, model: str, messages: list, **kwargs):
        """Generate a response from the model.
        
        Args:
            model: Model name/identifier.
            messages: List of message dicts with role and content.
            **kwargs: Additional provider-specific parameters.
            
        Returns:
            Provider response object.
        """
        pass

    @abstractmethod
    def health(self) -> dict:
        """Provider diagnostics and status.
        
        Returns:
            Dict with health information.
        """
        pass
