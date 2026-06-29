from rag.config.config import StepBackQueryTransformConfig
from rag.retrieval.query_transform.base import QueryTransformStrategy


class StepBackQueryTransformStrategy(QueryTransformStrategy):

    def __init__(self, config: StepBackQueryTransformConfig, provider):
        self.config = config
        self.provider = provider

    def run(self, ctx):
        """Generate a broader, higher-level version of the query."""
        prompt = f"""Rewrite the following question into a broader, higher-level question that would retrieve useful background knowledge.
The broader question should capture the general concept or category that the original question belongs to.
Return only the rewritten question, no additional text.

Original question: {ctx.query}

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

        # Use both original and broader query for retrieval
        ctx.dense_queries = [ctx.query, broader_query]
        ctx.sparse_queries = [ctx.query, broader_query]
        
        # Keep backward compatibility
        ctx.transformed_query = broader_query

        return ctx
