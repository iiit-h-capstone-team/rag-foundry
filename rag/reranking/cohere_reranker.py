import os
from rag.config.config import CohereRerankerConfig
from rag.reranking.base import RerankerStrategy


class CohereRerankerStrategy(RerankerStrategy):

    DEFAULT_MODEL = "rerank-v3.5"

    def __init__(
        self,
        config: CohereRerankerConfig
    ):
        self.config = config
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import cohere
            api_key = os.environ.get("COHERE_API_KEY")
            if not api_key:
                raise ValueError(
                    "COHERE_API_KEY environment variable is required for CohereRerankerStrategy"
                )
            self._client = cohere.Client(api_key=api_key)
        return self._client

    def rerank(
        self,
        query,
        texts
    ):
        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=[{"text": text} for text in texts],
            top_n=self.config.top_n
        )

        results = response.results
        scores = [0.0] * len(texts)

        for result in results:
            scores[result.index] = result.relevance_score

        return scores
