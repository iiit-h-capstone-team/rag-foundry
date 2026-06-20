from rag.generation.base import GenerationStrategy


class OpenAIGenerationStrategy(GenerationStrategy):

    def __init__(
        self,
        client,
        model: str = "gpt-4"
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
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
