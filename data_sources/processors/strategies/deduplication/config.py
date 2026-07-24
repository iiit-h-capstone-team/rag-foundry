"""Deduplication step configuration."""

from dataclasses import dataclass


@dataclass
class DeduplicationConfig:
    """Configuration for the deduplication processing step.

    Attributes:
        strategy: Deduplication key strategy.
            - ``content_hash``: deduplicate by content text only.
            - ``title_content_hash``: deduplicate by (title, content) pair.
    """
    strategy: str = "content_hash"
