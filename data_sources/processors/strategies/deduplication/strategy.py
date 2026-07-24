"""Deduplication processing step implementation."""

import hashlib
import logging
from typing import List

from data_sources.processors.base import ProcessingStep
from data_sources.processors.registry import processing_step_registry
from data_sources.processors.enums import ProcessingStepType
from data_sources.processors.strategies.deduplication.config import DeduplicationConfig
from rag.models.document import Document

logger = logging.getLogger(__name__)


@processing_step_registry.register(ProcessingStepType.DEDUPLICATION)
class DeduplicationStep(ProcessingStep):
    """Remove duplicate documents based on content hashing.

    Keeps the first occurrence and discards subsequent duplicates.
    """

    def __init__(self, config: DeduplicationConfig):
        super().__init__(config)

    def _hash_key(self, doc: Document) -> str:
        """Compute a deduplication key for a document."""
        if self.config.strategy == "title_content_hash":
            raw = f"{doc.title}||{doc.content}"
        else:
            raw = doc.content
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def process(self, documents: List[Document]) -> List[Document]:
        """Deduplicate documents, keeping first occurrence."""
        seen = set()
        unique = []
        for doc in documents:
            key = self._hash_key(doc)
            if key not in seen:
                seen.add(key)
                unique.append(doc)

        removed = len(documents) - len(unique)
        if removed:
            logger.info(
                "Deduplication (%s): removed %d duplicates, %d → %d documents",
                self.config.strategy, removed, len(documents), len(unique),
            )
        else:
            logger.info("Deduplication: no duplicates found (%d documents)", len(documents))

        return unique
