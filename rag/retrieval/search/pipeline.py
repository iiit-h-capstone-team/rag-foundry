from rag.retrieval.context import RetrievalContext
from rag.retrieval.search.base import SearchStrategy


class SearchPipeline:
    """Runs one or more search strategies and collects their ranked lists."""

    def __init__(self, strategies: list[SearchStrategy]):
        if not strategies:
            raise ValueError("SearchPipeline requires at least one search strategy")
        self.strategies = strategies

    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        # Determine which queries to use for each strategy
        # Use new dense_queries/sparse_queries if available, fall back to transformed_query or query
        ctx.search_results = []
        
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__.lower()
            
            if 'dense' in strategy_name:
                queries = ctx.dense_queries if ctx.dense_queries else [ctx.transformed_query or ctx.query]
            elif 'sparse' in strategy_name:
                queries = ctx.sparse_queries if ctx.sparse_queries else [ctx.transformed_query or ctx.query]
            else:
                # Default fallback
                queries = [ctx.transformed_query or ctx.query]
            
            result = strategy.search(queries)
            ctx.search_results.append(result)
        
        return ctx
