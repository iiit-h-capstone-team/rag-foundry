from rag.config.config import FusionConfig, QueryTransformConfig, RerankerConfig, RetrievalConfig
from rag.config.enums import FusionType, QueryTransformType
from providers.provider_factory import ProviderFactory
from rag.reranking.reranking_factory import RerankingFactory
from rag.retrieval.fusion.fusion_factory import FusionFactory
from rag.retrieval.pipeline import RetrievalPipeline
from rag.retrieval.query_transform.query_transform_factory import QueryTransformFactory
from rag.retrieval.rerank.noop import NoOpRetrievalRerankStage
from rag.retrieval.rerank.stage import RerankerRetrievalStage
from rag.retrieval.search.search_factory import SearchFactory


class RetrievalFactory:

    @staticmethod
    def create_retrieval_rerank(
        config: RerankerConfig | None,
    ):
        if config is None:
            return NoOpRetrievalRerankStage()

        reranker = RerankingFactory.create_reranker(config)
        return RerankerRetrievalStage(
            reranker=reranker,
            config=config.config,
        )

    
    @staticmethod
    def create_retrieval_pipeline(
        config: RetrievalConfig,
        *,
        embedder,
        vector_store,
        bm25_store=None,
        providers=None,
    ):
        query_transform_config = config.query_transform or QueryTransformConfig(
            type=QueryTransformType.NOOP
        )
        fusion_config = config.fusion or FusionConfig(
            type=FusionType.NOOP
        )

        # Resolve provider for query transform if configured
        provider = None
        if query_transform_config.provider and providers:
            provider_config = providers.get(query_transform_config.provider)
            if provider_config:
                provider = ProviderFactory.create_provider(
                    provider_name=query_transform_config.provider,
                    provider_type=provider_config.type,
                    config=provider_config
                )

        return RetrievalPipeline(
            query_transform=QueryTransformFactory.create_query_transform(
                query_transform_config,
                provider=provider
            ),
            search=SearchFactory.create_search_pipeline(
                config.search,
                embedder=embedder,
                vector_store=vector_store,
                bm25_store=bm25_store,
            ),
            fusion=FusionFactory.create_fusion(fusion_config),
            rerank=RetrievalFactory.create_retrieval_rerank(config.rerank),
        )