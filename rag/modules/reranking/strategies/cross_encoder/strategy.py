"""Cross-encoder reranking strategy implementation."""

from rag.modules.reranking.base import RerankerStrategy
from rag.modules.reranking.registry import reranking_registry
from rag.modules.reranking.enums import RerankingType
from rag.modules.reranking.strategies.cross_encoder.config import CrossEncoderRerankingConfig
from rag.runtime.model_cache import get_cross_encoder


@reranking_registry.register(RerankingType.CROSS_ENCODER)
class CrossEncoderRerankingStrategy(RerankerStrategy):
    """Cross-encoder reranking strategy using sentence transformers.
    
    Reranks documents using a cross-encoder model from sentence transformers.
    """

    def __init__(self, config: CrossEncoderRerankingConfig):
        super().__init__(config)
        
        if not self.config.model_name:
            raise ValueError(
                "CrossEncoderRerankingStrategy requires 'model_name' "
                "in the reranker config."
            )
        
        self.model = get_cross_encoder(self.config.model_name)

    def rerank(self, query, texts):
        """Rerank texts based on relevance to query.

        Args:
            query: User's question
            texts: List of texts to rerank

        Returns:
            List of relevance scores
        """
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return [float(score) for score in scores]
