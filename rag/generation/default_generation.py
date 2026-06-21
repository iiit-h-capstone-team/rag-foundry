from rag.config.config import GenerationConfig
from rag.generation.base import GenerationStrategy


class DefaultGenerationStrategy(GenerationStrategy):

    def __init__(
        self,
        config: GenerationConfig,
        provider,
    ):
        self.config = config
        self.provider = provider

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:

        messages = []

        if self.config.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.config.system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": f"""Based on the following context, answer the question.

Context:
{context}

Question:
{query}

Answer:""",
            }
        )

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content
