"""Voyage reranking strategy implementation."""

import os
from rag.modules.reranking.base import RerankerStrategy
from rag.modules.reranking.registry import reranking_registry
from rag.modules.reranking.enums import RerankingType
from rag.modules.reranking.strategies.voyage.config import VoyageRerankingConfig


@reranking_registry.register(RerankingType.VOYAGE)
class VoyageRerankingStrategy(RerankerStrategy):
    """Voyage reranking strategy using Voyage API.
    
    Reranks documents using the Voyage reranking API.
    """

    DEFAULT_MODEL = "rerank-2"

    def __init__(self, config: VoyageRerankingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import voyageai
            api_key = os.environ.get("VOYAGE_API_KEY")
            if not api_key:
                raise ValueError(
                    "VOYAGE_API_KEY environment variable is required for VoyageRerankingStrategy"
                )
            voyageai.api_key = api_key
            self._client = voyageai.Client()
        return self._client

    def rerank(self, query, texts):
        """Rerank texts based on relevance to query.

        Args:
            query: User's question
            texts: List of texts to rerank

        Returns:
            List of relevance scores
        """
        response = self._client.rerank(
            query=query,
            documents=texts,
            model=self.model,
            top_k=self.config.top_k
        )

        scores = [0.0] * len(texts)
        for result in response.results:
            scores[result.index] = result.relevance_score

        return scores
