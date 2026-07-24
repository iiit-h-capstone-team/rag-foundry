"""Processing step registry."""

from core.registry import BaseRegistry
from data_sources.processors.base import ProcessingStep

processing_step_registry = BaseRegistry[ProcessingStep]()
