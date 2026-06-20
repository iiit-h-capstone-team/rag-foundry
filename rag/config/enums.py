from enum import Enum

class ChunkingType(str, Enum):
    SENTENCE = "sentence"
    FIXED_WINDOW = "fixed_window"
    TOKEN = "token"


class EmbeddingType(str, Enum):
    BGE = "bge"
    OPENAI = "openai"
    LOCAL = "local"


class RetrievalType(str, Enum):
    DENSE_RERANK = "dense_rerank"
    DENSE = "dense"
    HYBRID = "hybrid"


class VectorStoreType(str, Enum):
    FAISS = "faiss"


class GenerationType(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"


class EvaluationType(str, Enum):
    TRACE = "trace"
