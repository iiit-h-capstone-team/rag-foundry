import os
from rag.config.config import VoyageRerankerConfig
from rag.reranking.base import RerankerStrategy


class VoyageRerankerStrategy(RerankerStrategy):

    DEFAULT_MODEL = "rerank-2"

    def __init__(
        self,
        config: VoyageRerankerConfig
    ):
        self.config = config
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
                    "VOYAGE_API_KEY environment variable is required for VoyageRerankerStrategy"
                )
            voyageai.api_key = api_key
            self._client = voyageai.Client()
        return self._client

    def rerank(
        self,
        query,
        texts
    ):
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
