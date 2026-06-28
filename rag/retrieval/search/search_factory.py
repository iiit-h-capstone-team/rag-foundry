from rag.config.config import SearchPipelineConfig, SearchStrategyConfig
from rag.config.enums import SearchType
from rag.retrieval.search.dense import DenseSearchStrategy
from rag.retrieval.search.sparse import SparseSearchStrategy
from rag.retrieval.search.pipeline import SearchPipeline


class SearchFactory:
    
    @staticmethod
    def create_search_strategy(
        config: SearchStrategyConfig,
        *,
        embedder,
        vector_store,
        bm25_store=None,
    ):
        strategies = {
            SearchType.DENSE: lambda: DenseSearchStrategy(
                config=config.config,
                embedder=embedder,
                vector_store=vector_store,
            ),
            SearchType.SPARSE: lambda: SparseSearchStrategy(
                config=config.config,
                vector_store=vector_store,
                bm25_store=bm25_store,
            ),
        }
        return strategies[config.type]()

    @staticmethod
    def create_search_pipeline(
        config: SearchPipelineConfig,
        *,
        embedder,
        vector_store,
        bm25_store=None,
    ):
        strategies = [
            SearchFactory.create_search_strategy(
                search_config,
                embedder=embedder,
                vector_store=vector_store,
                bm25_store=bm25_store,
            )
            for search_config in config.searches
        ]
        return SearchPipeline(strategies)