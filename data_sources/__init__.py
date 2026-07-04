"""Datasets package for data loading and processing.

Handles dataset loading from various sources and processing raw samples
into canonical Document objects via parsers.

Flow:
    Dataset Source → DatasetLoader (loaders/) → Raw Samples
    → DataProcessor (processors/) → ParsingStrategy (parsers/) → Document
"""

from data_sources.loaders.base import DatasetLoader, DatasetLoadingConfig
from data_sources.loaders.registry import loader_registry, LoaderRegistry
from data_sources.loaders.enums import LoaderType
from data_sources.processors.data_processor import DataProcessor

# Lazy import of HuggingFaceLoader
def __getattr__(name):
    if name == "HuggingFaceLoader":
        from data_sources.loaders.huggingface_loader import HuggingFaceLoader
        return HuggingFaceLoader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DatasetLoader",
    "DatasetLoadingConfig",
    "LoaderRegistry",
    "loader_registry",
    "LoaderType",
    "DataProcessor",
    "HuggingFaceLoader",
]
