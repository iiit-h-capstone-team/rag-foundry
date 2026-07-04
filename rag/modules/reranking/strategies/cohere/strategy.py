"""Cohere reranking strategy implementation."""

from rag.modules.reranking.base import RerankerStrategy
from rag.modules.reranking.registry import reranking_registry
from rag.modules.reranking.enums import RerankingType
from rag.modules.reranking.strategies.cohere.config import CohereRerankingConfig


@reranking_registry.register(RerankingType.COHERE)
class CohereRerankingStrategy(RerankerStrategy):
    """Cohere reranking strategy using Cohere API.
    
    Reranks documents based on relevance to query using Cohere's rerank model.
    """

    def __init__(self, config: CohereRerankingConfig, provider):
        super().__init__(config)
        self.provider = provider

    def rerank(self, query, texts):
        """Rerank texts based on relevance to query.

        Args:
            query: User's question
            texts: List of texts to rerank

        Returns:
            List of reranked texts with scores
        """
        results = self.provider.rerank(
            model=self.config.model,
            query=query,
            documents=texts,
            top_n=self.config.top_n
        )
        
        return results
