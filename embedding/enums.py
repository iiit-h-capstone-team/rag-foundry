"""Embedding strategy type enumerations."""

from enum import Enum


class EmbeddingType(str, Enum):
    """Available embedding strategies."""
    SENTENCE_TRANSFORMER = "sentence_transformer"
    OPENAI = "openai"
    OLLAMA = "ollama"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    MEDCPT = "medcpt"
