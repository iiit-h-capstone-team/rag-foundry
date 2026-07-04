"""Base search strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class SearchStrategy(BaseStrategy):
    """Base class for search strategies."""

    @abstractmethod
    def search(self, queries: list[str]) -> list[dict]:
        """Return one ranked list of candidate chunks for the queries.
        
        Accepts a list of queries and merges results from all queries,
        deduplicating by chunk index and keeping the best score per chunk.
        
        Args:
            queries: List of query strings.
            
        Returns:
            List of result dicts with keys: index, chunk, score, and strategy-specific scores.
        """
        pass
