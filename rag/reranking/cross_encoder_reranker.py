from rag.config.config import RerankerConfig
from rag.reranking.base import RerankerStrategy


class CrossEncoderRerankerStrategy(RerankerStrategy):

    def __init__(
        self,
        config: RerankerConfig
    ):
        self.config = config

        if not self.config.model_name:
            raise ValueError(
                "CrossEncoderRerankerStrategy requires 'model_name' "
                "in the reranker config."
            )

        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(self.config.model_name)

    def rerank(
        self,
        query,
        texts
    ):
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return [float(score) for score in scores]
