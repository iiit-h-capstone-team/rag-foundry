from abc import ABC, abstractmethod


class EvaluationStrategy(ABC):

    @abstractmethod
    def evaluate(
        self,
        query: str,
        retrieved_docs,
        response: str
    ) -> dict:
        pass
