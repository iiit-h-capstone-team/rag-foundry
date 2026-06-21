from abc import ABC, abstractmethod


class GenerationStrategy(ABC):

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
        **kwargs,
    ) -> str:
        pass