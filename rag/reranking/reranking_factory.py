from rag.config.config import RerankerConfig
from rag.config.enums import RerankerType
from rag.reranking.cross_encoder_reranker import CrossEncoderRerankerStrategy
from rag.reranking.cohere_reranker import CohereRerankerStrategy
from rag.reranking.voyage_reranker import VoyageRerankerStrategy
from rag.reranking.jina_reranker import JinaRerankerStrategy
from rag.reranking.mixedbread_reranker import MixedBreadRerankerStrategy

class RerankingFactory:
    
    @staticmethod
    def create_reranker(
        config: RerankerConfig,
        **kwargs
    ):
        strategies = {
            RerankerType.CROSS_ENCODER: lambda: CrossEncoderRerankerStrategy(
                config=config.config
            ),
            RerankerType.COHERE: lambda: CohereRerankerStrategy(
                config=config.config
            ),
            RerankerType.VOYAGE: lambda: VoyageRerankerStrategy(
                config=config.config
            ),
            RerankerType.JINA: lambda: JinaRerankerStrategy(
                config=config.config
            ),
            RerankerType.MIXEDBREAD: lambda: MixedBreadRerankerStrategy(
                config=config.config
            )
        }
        return strategies[config.type]()