"""MixedBread reranking strategy implementation."""

import os
from rag.modules.reranking.base import RerankerStrategy
from rag.modules.reranking.registry import reranking_registry
from rag.modules.reranking.enums import RerankingType
from rag.modules.reranking.strategies.mixedbread.config import MixedBreadRerankingConfig


@reranking_registry.register(RerankingType.MIXEDBREAD)
class MixedBreadRerankingStrategy(RerankerStrategy):
    """MixedBread reranking strategy using MixedBread API.
    
    Reranks documents using the MixedBread reranking API.
    """

    DEFAULT_MODEL = "mxbai-rerank-large-v1"

    def __init__(self, config: MixedBreadRerankingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import requests
            api_key = os.environ.get("MIXEDBREAD_API_KEY")
            if not api_key:
                raise ValueError(
                    "MIXEDBREAD_API_KEY environment variable is required for MixedBreadRerankingStrategy"
                )
            self._client = requests.Session()
            self._client.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
        return self._client

    def rerank(self, query, texts):
        """Rerank texts based on relevance to query.

        Args:
            query: User's question
            texts: List of texts to rerank

        Returns:
            List of relevance scores
        """
        response = self.client.post(
            "https://api.mixedbread.ai/v1/reranking",
            json={
                "model": self.model,
                "query": query,
                "documents": texts,
                "top_n": self.config.top_n
            }
        )
        response.raise_for_status()

        result = response.json()
        scores = [0.0] * len(texts)

        for item in result.get("results", []):
            scores[item["index"]] = item["relevance_score"]

        return scores
