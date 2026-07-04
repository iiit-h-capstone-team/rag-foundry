"""Base fusion strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class FusionStrategy(BaseStrategy):
    """Base class for fusion strategies."""

    @abstractmethod
    def fuse(self, search_results: list[list[dict]]) -> list[dict]:
        """Combine search result lists into a single ranked list.
        
        Args:
            search_results: List of result lists from different search strategies.
            
        Returns:
            Single ranked list of fused results.
        """
        pass
