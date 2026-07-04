"""Dataset loader strategy registry."""

from core.registry import BaseRegistry
from data_sources.loaders.base import DatasetLoader


class LoaderRegistry(BaseRegistry[DatasetLoader]):
    """Registry for dataset loader strategy plugins."""
    pass


loader_registry = LoaderRegistry()
