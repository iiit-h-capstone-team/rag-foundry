"""RAG pipeline strategy modules.

Each module follows the registry+decorator pattern and provides pluggable
strategies for a specific pipeline stage.

Available modules:
    - chunking: Document chunking strategies
    - search: Search strategies (dense, sparse)
    - fusion: Result fusion strategies (RRF, weighted sum)
    - query_transform: Query transformation strategies (HyDE, multi-query)
    - reranking: Reranking strategies (cross-encoder, etc.)
    - generation: Response generation strategies
"""

from rag.modules.chunking.registry import chunking_registry
from rag.modules.search.registry import search_registry
from rag.modules.fusion.registry import fusion_registry
from rag.modules.query_transform.registry import query_transform_registry
from rag.modules.reranking.registry import reranking_registry
from rag.modules.generation.registry import generation_registry


__all__ = [
    "chunking_registry",
    "search_registry",
    "fusion_registry",
    "query_transform_registry",
    "reranking_registry",
    "generation_registry",
]
