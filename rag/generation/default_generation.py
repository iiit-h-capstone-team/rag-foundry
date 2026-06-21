from rag.generation.base import GenerationStrategy


class DefaultGenerationStrategy(GenerationStrategy):

    def __init__(
        self,
        provider,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        query: str,
        context: str,
        **kwargs,
    ) -> str:

        temperature = kwargs.get(
            "temperature",
            self.temperature,
        )

        max_tokens = kwargs.get(
            "max_tokens",
            self.max_tokens,
        )

        messages = []

        if self.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt,
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
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content