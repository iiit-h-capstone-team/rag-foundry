"""Dataset loaders with registry-based strategy architecture."""

from data_sources.loaders.base import DatasetLoader, DatasetLoadingConfig
from data_sources.loaders.registry import loader_registry, LoaderRegistry
from data_sources.loaders.enums import LoaderType

# Eagerly import to trigger @register decorator; guarded for missing datasets
try:
    from data_sources.loaders.huggingface_loader import HuggingFaceLoader
except ImportError:
    pass


__all__ = [
    "DatasetLoader",
    "DatasetLoadingConfig",
    "LoaderRegistry",
    "loader_registry",
    "LoaderType",
    "HuggingFaceLoader",
]
