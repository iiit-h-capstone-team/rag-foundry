"""MedCPT embedding strategy implementation."""

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.medcpt.config import MedCPTEmbeddingConfig
from rag.runtime.model_cache import get_sentence_transformer


@embedding_registry.register(EmbeddingType.MEDCPT)
class MedCPTEmbeddingStrategy(EmbeddingStrategy):
    """MedCPT embedding strategy using separate query and article encoders.

    This strategy is designed for biomedical text and uses two separate models:
    - Query encoder for search queries
    - Article encoder for documents/passages
    """

    def __init__(self, config: MedCPTEmbeddingConfig):
        super().__init__(config)
        self.query_model = get_sentence_transformer(self.config.query_model_name)
        self.article_model = get_sentence_transformer(self.config.article_model_name)

    def embed(self, texts, is_query=False):
        """Embed texts using the appropriate encoder.

        Args:
            texts: Single text string or list of texts to embed
            is_query: If True, use query encoder; if False, use article encoder
        """
        if isinstance(texts, str):
            texts = [texts]

        model = self.query_model if is_query else self.article_model

        return model.encode(texts, normalize_embeddings=True)

    def embed_query(self, query):
        """Embed a single query using the query encoder."""
        return self.embed(query, is_query=True)

    def embed_documents(self, documents):
        """Embed documents using the article encoder."""
        return self.embed(documents, is_query=False)
