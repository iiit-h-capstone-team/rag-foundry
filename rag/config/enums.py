from enum import Enum


class Mode(str, Enum):
    """Runtime mode controlling pipeline logging verbosity."""
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class ProviderType(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class ChunkingType(str, Enum):
    SENTENCE = "sentence"
    FIXED_WINDOW = "fixed_window"
    TOKEN = "token"
    SEMANTIC = "semantic"


class EmbeddingType(str, Enum):
    SENTENCE_TRANSFORMER = "sentence_transformer"
    OPENAI = "openai"
    OLLAMA = "ollama"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    MEDCPT = "medcpt"


class RetrievalType(str, Enum):
    DENSE_RERANK = "dense_rerank"
    DENSE = "dense"
    HYBRID = "hybrid"


class RerankerType(str, Enum):
    CROSS_ENCODER = "cross_encoder"
    COHERE = "cohere"
    VOYAGE = "voyage"
    JINA = "jina"
    MIXEDBREAD = "mixedbread"


class VectorStoreType(str, Enum):
    FAISS = "faiss"


class GenerationType(str, Enum):
    DEFAULT = "default"


class EvaluationType(str, Enum):
    TRACE = "trace"
