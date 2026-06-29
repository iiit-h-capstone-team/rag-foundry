from functools import lru_cache

from sentence_transformers import CrossEncoder, SentenceTransformer


@lru_cache(maxsize=None)
def get_sentence_transformer(model_name: str):
    print(f"Loading embedding model: {model_name}")
    return SentenceTransformer(model_name)


@lru_cache(maxsize=None)
def get_cross_encoder(model_name: str):
    print(f"Loading reranker model: {model_name}")
    return CrossEncoder(model_name)


# Note: API-based providers (Ollama, Cohere, Voyage, HuggingFace Inference, Jina, MixedBread)
# use lazy client initialization within their strategy classes and do not require
# model caching. MedCPT reuses the get_sentence_transformer cache for its encoders.