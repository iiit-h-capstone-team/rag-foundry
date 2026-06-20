from rag.reranking.base import RerankerStrategy


class CrossEncoderRerankerStrategy(RerankerStrategy):

    def __init__(
        self,
        model=None,
        model_name=None
    ):
        if isinstance(model, str):
            model_name = model
            model = None

        if model is None:
            if model_name is None:
                raise ValueError(
                    "CrossEncoderRerankerStrategy requires either a preloaded "
                    "`model` object or a `model_name` to load."
                )
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(model_name)

        self.model = model

    def rerank(
        self,
        query,
        texts
    ):
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return [float(score) for score in scores]
