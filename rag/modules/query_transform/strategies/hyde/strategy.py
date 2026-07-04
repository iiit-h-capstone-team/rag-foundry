"""HyDE query transform strategy implementation."""

from rag.modules.query_transform.base import QueryTransformStrategy, QueryTransformResult
from rag.modules.query_transform.registry import query_transform_registry
from rag.modules.query_transform.enums import QueryTransformType
from rag.modules.query_transform.strategies.hyde.config import HyDEQueryTransformConfig


@query_transform_registry.register(QueryTransformType.HYDE)
class HyDEQueryTransformStrategy(QueryTransformStrategy):
    """HyDE (Hypothetical Document Embeddings) query transform."""

    def __init__(self, config: HyDEQueryTransformConfig, provider):
        super().__init__(config)
        self.provider = provider

    def transform(self, query: str) -> QueryTransformResult:
        """Generate a hypothetical document for dense retrieval."""
        prompt = f"""Write a detailed, factual passage that would likely answer the following question. 
The passage should be information-rich and written in a style suitable for semantic retrieval.
Do not answer conversationally. Focus on providing accurate, comprehensive information.

Question: {query}

Passage:"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        hypothetical_document = response.choices[0].message.content.strip()

        return QueryTransformResult(
            dense_queries=[hypothetical_document],
            sparse_queries=[query],
        )
