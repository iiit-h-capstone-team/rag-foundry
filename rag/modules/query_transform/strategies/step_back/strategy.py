"""Step-Back query transform strategy implementation."""

from rag.modules.query_transform.base import QueryTransformStrategy, QueryTransformResult
from rag.modules.query_transform.registry import query_transform_registry
from rag.modules.query_transform.enums import QueryTransformType
from rag.modules.query_transform.strategies.step_back.config import StepBackQueryTransformConfig


@query_transform_registry.register(QueryTransformType.STEP_BACK)
class StepBackQueryTransformStrategy(QueryTransformStrategy):
    """Step-Back query transform: generates broader, higher-level queries."""

    def __init__(self, config: StepBackQueryTransformConfig, provider):
        super().__init__(config)
        self.provider = provider

    def transform(self, query: str) -> QueryTransformResult:
        """Generate a broader, higher-level version of the query."""
        prompt = f"""Rewrite the following question into a broader, higher-level question that would retrieve useful background knowledge.
The broader question should capture the general concept or category that the original question belongs to.
Return only the rewritten question, no additional text.

Original question: {query}

Broader question:"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        broader_query = response.choices[0].message.content.strip()

        return QueryTransformResult(
            dense_queries=[query, broader_query],
            sparse_queries=[query, broader_query],
        )
