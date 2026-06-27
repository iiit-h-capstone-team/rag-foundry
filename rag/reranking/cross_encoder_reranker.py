from rag.config.config import CrossEncoderRerankerConfig
from rag.reranking.base import RerankerStrategy
from rag.runtime.model_cache import get_cross_encoder


class CrossEncoderRerankerStrategy(RerankerStrategy):

    def __init__(
        self,
        config: CrossEncoderRerankerConfig
    ):
        self.config = config

        if not self.config.model_name:
            raise ValueError(
                "CrossEncoderRerankerStrategy requires 'model_name' "
                "in the reranker config."
            )

        self.model =  get_cross_encoder(self.config.model_name)

    def rerank(
        self,
        query,
        texts
    ):
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return [float(score) for score in scores]
