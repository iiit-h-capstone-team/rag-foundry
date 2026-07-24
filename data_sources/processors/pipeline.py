"""Processing pipeline for composing multiple processing steps."""

import logging
from typing import List

from data_sources.processors.base import ProcessingStep
from rag.models.document import Document

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """Runs a sequence of processing steps on a document list.

    Each step receives the output of the previous step and returns
    a (possibly filtered or augmented) list of documents.
    """

    def __init__(self, steps: List[ProcessingStep]):
        self.steps = steps

    def run(self, documents: List[Document]) -> List[Document]:
        """Execute all steps in sequence.

        Args:
            documents: Initial document list.

        Returns:
            Processed document list after all steps.
        """
        for step in self.steps:
            step_name = step.__class__.__name__
            before = len(documents)
            documents = step.process(documents)
            logger.debug(
                "ProcessingPipeline [%s]: %d → %d documents",
                step_name, before, len(documents),
            )
        return documents

    @classmethod
    def from_config(cls, config: dict) -> "ProcessingPipeline":
        """Build a pipeline from experiment YAML config.

        Expected format::

            data_processing:
              steps:
                - type: deduplication
                  config:
                    strategy: content_hash

        Args:
            config: The ``data_processing`` dict from experiment config.

        Returns:
            ProcessingPipeline instance.
        """
        from data_sources.processors.registry import processing_step_registry
        # Trigger strategy registration
        import data_sources.processors.strategies.deduplication  # noqa: F401

        steps_config = config.get("steps", [])
        steps = []
        for step_cfg in steps_config:
            step_type = step_cfg.get("type")
            step_config = step_cfg.get("config", {})
            step = processing_step_registry.create(
                step_type,
                config=step_config,
            )
            steps.append(step)

        logger.info("ProcessingPipeline built with %d steps: %s",
                     len(steps), [s.__class__.__name__ for s in steps])
        return cls(steps)
