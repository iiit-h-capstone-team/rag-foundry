import os
from rag.config.config import JinaRerankerConfig
from rag.reranking.base import RerankerStrategy


class JinaRerankerStrategy(RerankerStrategy):

    DEFAULT_MODEL = "jina-reranker-v2-base"

    def __init__(
        self,
        config: JinaRerankerConfig
    ):
        self.config = config
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import requests
            api_key = os.environ.get("JINA_API_KEY")
            if not api_key:
                raise ValueError(
                    "JINA_API_KEY environment variable is required for JinaRerankerStrategy"
                )
            self._client = requests.Session()
            self._client.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
        return self._client

    def rerank(
        self,
        query,
        texts
    ):
        response = self.client.post(
            "https://api.jina.ai/v1/rerank",
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
