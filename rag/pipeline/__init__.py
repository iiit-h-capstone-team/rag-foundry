"""RAG pipeline orchestration."""

from rag.pipeline.context import RetrievalContext
from rag.pipeline.search_pipeline import SearchPipeline
from rag.pipeline.retrieval_pipeline import RetrievalPipeline

# RAGPipeline imported lazily to avoid numpy dependency at import time
def __getattr__(name):
    if name == "RAGPipeline":
        from rag.pipeline.rag_pipeline import RAGPipeline
        return RAGPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "RetrievalContext",
    "SearchPipeline",
    "RetrievalPipeline",
    "RAGPipeline",
]
