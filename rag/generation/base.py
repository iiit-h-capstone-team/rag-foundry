from abc import ABC, abstractmethod


class GenerationStrategy(ABC):

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        pass
