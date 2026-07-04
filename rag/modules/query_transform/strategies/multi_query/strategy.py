"""MultiQuery query transform strategy implementation."""

from rag.modules.query_transform.base import QueryTransformStrategy, QueryTransformResult
from rag.modules.query_transform.registry import query_transform_registry
from rag.modules.query_transform.enums import QueryTransformType
from rag.modules.query_transform.strategies.multi_query.config import MultiQueryQueryTransformConfig


@query_transform_registry.register(QueryTransformType.MULTI_QUERY)
class MultiQueryQueryTransformStrategy(QueryTransformStrategy):
    """MultiQuery query transform: generates multiple reformulations."""

    def __init__(self, config: MultiQueryQueryTransformConfig, provider):
        super().__init__(config)
        self.provider = provider

    def transform(self, query: str) -> QueryTransformResult:
        """Generate multiple semantically different reformulations of the query."""
        prompt = f"""Generate {self.config.num_queries} semantically different reformulations of the following question.
The reformulations should preserve meaning while varying wording and terminology.
Return one query per line, with no numbering or additional text.

Original question: {query}

Reformulations:"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        content = response.choices[0].message.content.strip()
        
        queries = [q.strip() for q in content.split('\n') if q.strip()]
        
        if len(queries) < self.config.num_queries:
            queries.append(query)
        
        queries = queries[:self.config.num_queries]

        return QueryTransformResult(
            dense_queries=queries,
            sparse_queries=queries,
        )
