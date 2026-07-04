"""Base evaluation strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class EvaluationStrategy(BaseStrategy):

    @abstractmethod
    def evaluate(
        self,
        query: str,
        retrieved_docs,
        response: str
    ) -> dict:
        pass
