"""No-op parser for raw text data.

This parser passes through raw text documents as-is, converting them into
canonical Document objects without any parsing or transformation. Useful for
datasets like PubMedQA where documents are already plain text with no
special structure (no title/passage separation).
"""

from typing import Dict, Any, Optional

from parsers.base import ParsingStrategy
from parsers.registry import parser_registry
from parsers.enums import ParserType


@parser_registry.register(ParserType.NOOP)
class NoopParser(ParsingStrategy):
    """Parser that passes through raw text as-is.

    Expected raw format:
        Plain text string (no special structure)

    Produces a Document where:
        - title: Empty string (no title extraction)
        - content: The raw text as-is
        - metadata: Provided metadata plus parser_type
    """

    def __init__(self, config=None):
        super().__init__(config)

    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Parse a raw text document by passing it through as-is."""
        if not raw_document:
            raise ValueError("raw_document cannot be None or empty")

        from rag.models.document import Document

        # Merge provided metadata with parser info
        final_metadata = metadata or {}
        final_metadata = {
            **final_metadata,
            'parser_type': 'noop'
        }

        return Document(
            title="",
            content=raw_document.strip(),
            metadata=final_metadata
        )
