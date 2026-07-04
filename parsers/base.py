"""Base parser strategy class."""

from abc import abstractmethod
from typing import Dict, Any, Optional

from core.strategy import BaseStrategy


class ParsingStrategy(BaseStrategy):
    """Base class for document parsing strategies.

    Each parsing strategy knows how to convert a raw document string
    into a canonical Document object. This allows the datasets layer
    to handle various data formats while downstream consumers remain
    format-agnostic.
    """

    @abstractmethod
    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Parse a raw document into a canonical Document object.

        Args:
            raw_document: Raw document string in the strategy's expected format.
            metadata: Optional metadata dictionary to attach to the document.

        Returns:
            Document: Canonical document object with title, content, and metadata.

        Raises:
            ValueError: If the raw_document cannot be parsed.
        """
        pass
