"""Base reranking strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class RerankerStrategy(BaseStrategy):

    @abstractmethod
    def rerank(
        self,
        query,
        texts
    ):
        """Return a relevance score for each text given the query."""
        pass
