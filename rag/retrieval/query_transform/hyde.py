from rag.config.config import HyDEQueryTransformConfig
from rag.retrieval.query_transform.base import QueryTransformStrategy


class HyDEQueryTransformStrategy(QueryTransformStrategy):

    def __init__(self, config: HyDEQueryTransformConfig, provider):
        self.config = config
        self.provider = provider

    def run(self, ctx):
        """Generate a hypothetical document for dense retrieval."""
        prompt = f"""Write a detailed, factual passage that would likely answer the following question. 
The passage should be information-rich and written in a style suitable for semantic retrieval.
Do not answer conversationally. Focus on providing accurate, comprehensive information.

Question: {ctx.query}

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

        # Use hypothetical document for dense retrieval, original query for sparse
        ctx.dense_queries = [hypothetical_document]
        ctx.sparse_queries = [ctx.query]
        
        # Keep backward compatibility
        ctx.transformed_query = hypothetical_document

        return ctx
