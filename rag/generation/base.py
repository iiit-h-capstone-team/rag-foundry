from abc import ABC, abstractmethod


class GenerationStrategy(ABC):

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        """Generate an answer for ``query`` grounded in ``context``.

        Generation parameters (model, temperature, max_tokens, system_prompt)
        are read from the strategy's stored config, not passed at call time.
        """
        pass