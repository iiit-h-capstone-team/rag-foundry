from rag.config.config import MultiQueryQueryTransformConfig
from rag.retrieval.query_transform.base import QueryTransformStrategy


class MultiQueryQueryTransformStrategy(QueryTransformStrategy):

    def __init__(self, config: MultiQueryQueryTransformConfig, provider):
        self.config = config
        self.provider = provider

    def run(self, ctx):
        """Generate multiple semantically different reformulations of the query."""
        prompt = f"""Generate {self.config.num_queries} semantically different reformulations of the following question.
The reformulations should preserve meaning while varying wording and terminology.
Return one query per line, with no numbering or additional text.

Original question: {ctx.query}

Reformulations:"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.provider.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=getattr(self.config, 'max_tokens', 512),
        )

        content = response.choices[0].message.content.strip()
        
        # Parse one query per line
        queries = [q.strip() for q in content.split('\n') if q.strip()]
        
        # Ensure we have the requested number of queries
        if len(queries) < self.config.num_queries:
            queries.append(ctx.query)
        
        queries = queries[:self.config.num_queries]

        # Use all reformulations for both dense and sparse retrieval
        ctx.dense_queries = queries
        ctx.sparse_queries = queries
        
        # Keep backward compatibility - use first reformulation
        ctx.transformed_query = queries[0]

        return ctx
