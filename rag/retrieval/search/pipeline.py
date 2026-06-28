from rag.retrieval.context import RetrievalContext
from rag.retrieval.search.base import SearchStrategy


class SearchPipeline:
    """Runs one or more search strategies and collects their ranked lists."""

    def __init__(self, strategies: list[SearchStrategy]):
        if not strategies:
            raise ValueError("SearchPipeline requires at least one search strategy")
        self.strategies = strategies

    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        query = ctx.transformed_query or ctx.query
        ctx.search_results = [
            strategy.search(query) for strategy in self.strategies
        ]
        return ctx
