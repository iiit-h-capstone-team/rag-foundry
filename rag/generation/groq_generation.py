from rag.generation.base import GenerationStrategy


class GroqGenerationStrategy(GenerationStrategy):

    def __init__(
        self,
        client,
        model: str = "llama-3.1-8b-instant"
    ):
        self.client = client
        self.model = model

    def generate(
        self,
        query: str,
        context: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:

        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
