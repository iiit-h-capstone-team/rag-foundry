"""Default generation strategy implementation."""

from rag.modules.generation.base import GenerationStrategy
from rag.modules.generation.registry import generation_registry
from rag.modules.generation.enums import GenerationType
from rag.modules.generation.strategies.default.config import DefaultGenerationConfig


@generation_registry.register(GenerationType.DEFAULT)
class DefaultGenerationStrategy(GenerationStrategy):
    """Default generation strategy that generates answers from context and query.
    
    Uses a provider (OpenAI, Ollama, etc.) as a pluggable component.
    """

    def __init__(self, config: DefaultGenerationConfig, provider):
        super().__init__(config)
        self.provider = provider

    def generate(self, query: str, context: str) -> str:
        """Generate an answer for query grounded in context.

        Args:
            query: User's question
            context: Retrieved context to ground the answer

        Returns:
            Generated answer string
        """
        messages = []

        if self.config.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.config.system_prompt,
                }
            )
        else:
            messages.append(
                {
                    "role": "system",
                    "content": """You are a knowledgeable and reliable AI assistant specializing in question answering.

Your primary objective is to provide accurate, concise, and well-supported answers based on the supplied context.

Guidelines:
- Base your answer only on the provided context.
- Do not use external knowledge or make unsupported assumptions.
- If the provided context does not contain enough information to answer the question, clearly state that the answer cannot be determined from the provided context.
- Do not fabricate facts or citations.
- Keep the answer focused on the user's question.
- Prefer factual correctness over completeness.
- If multiple pieces of retrieved context are relevant, synthesize them into a coherent answer.""",
                }
            )

        user_prompt_content = f"""You are given a set of retrieved context passages and a question.

Retrieved Context:
--------------------
{context}
--------------------

Question:
{query}

Using only the retrieved context, answer the question as accurately and concisely as possible.

If the answer cannot be determined from the provided context, explicitly state that the information is not available in the retrieved context.

Answer:"""

        if self.config.user_prompt:
            user_prompt_content = self.config.user_prompt

        user_prompt = {
            "role": "user",
            "content": user_prompt_content.format(
                context=context,
                query=query,
            ),
        }

        messages.append(user_prompt)

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content
