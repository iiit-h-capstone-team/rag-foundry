"""
Ingestion package for RAG system.

This package handles dataset loading, document parsing, and preprocessing.
The ingestion layer is separated from the RAG layer to ensure:
- Single Responsibility: Ingestion handles data sources, RAG handles retrieval
- Open/Closed Principle: Easy to add new data sources without modifying RAG code
- Dependency Inversion: RAG depends on canonical Document objects, not data formats
- Extensibility: Support for PDFs, Confluence, Slack, JSON, Markdown, etc.

The flow is:
    Dataset Source
        ↓
    DatasetLoader (loaders/)
        ↓
    Raw Samples (List[Dict])
        ↓
    DataProcessor (processors/)
        ↓
    ParsingStrategy (parsers/)
        ↓
    Document (canonical rag.models.Document)
        ↓
    RAG Pipeline (chunking, embedding, retrieval, generation)
"""

# Parsers (no external dependencies)
from .parsers.base import ParsingStrategy
from .parsers.title_passage_parser import TitlePassageParser
from .parsers.strategy_factory import ParserFactory, ParserType

# Processors (no external dependencies)
from .processors.data_processor import DataProcessor

# Loaders (may have external dependencies, imported conditionally)
try:
    from .loaders.base import DatasetLoader, DatasetLoadingConfig
    from .loaders.ragbench_loader import (
        RAGBenchLoader,
        RAGBenchCovidQALoader,
        RAGBenchFeverousLoader,
        RAGBenchHotpotQALoader
    )
    _loaders_available = True
except ImportError:
    # Loaders require external dependencies (e.g., datasets)
    # They will be available when dependencies are installed
    _loaders_available = False
    DatasetLoader = None
    DatasetLoadingConfig = None
    RAGBenchLoader = None
    RAGBenchCovidQALoader = None
    RAGBenchFeverousLoader = None
    RAGBenchHotpotQALoader = None

__all__ = [
    # Parsers
    'ParsingStrategy',
    'TitlePassageParser',
    'ParserFactory',
    'ParserType',
    # Processors
    'DataProcessor',
]

# Add loaders to __all__ if available
if _loaders_available:
    __all__.extend([
        'DatasetLoader',
        'DatasetLoadingConfig',
        'RAGBenchLoader',
        'RAGBenchCovidQALoader',
        'RAGBenchFeverousLoader',
        'RAGBenchHotpotQALoader',
    ])
