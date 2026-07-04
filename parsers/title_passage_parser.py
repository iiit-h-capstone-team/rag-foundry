"""Title/Passage parser implementation."""

import re
from typing import Dict, Any, Optional

from parsers.base import ParsingStrategy
from parsers.registry import parser_registry
from parsers.enums import ParserType


@parser_registry.register(ParserType.TITLE_PASSAGE)
class TitlePassageParser(ParsingStrategy):
    """Parser for documents with Title and Passage format.

    Expected format:
        Title: <title text>
        Passage: <passage text>
    """

    def __init__(self, config=None):
        super().__init__(config)

    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Parse a document with Title and Passage format."""
        if not raw_document:
            raise ValueError("raw_document cannot be None or empty")

        # Import Document here to avoid circular imports
        from rag.models.document import Document

        # Extract title
        title_match = re.search(
            r"Title:\s*(.*?)\n",
            raw_document,
            re.DOTALL
        )

        # Extract passage
        passage_match = re.search(
            r"Passage:\s*(.*)",
            raw_document,
            re.DOTALL
        )

        title = (
            title_match.group(1).strip()
            if title_match else ""
        )

        content = (
            passage_match.group(1).strip()
            if passage_match else raw_document.strip()
        )

        # Merge provided metadata with extracted info
        final_metadata = metadata or {}
        final_metadata = {
            **final_metadata,
            'parser_type': 'title_passage'
        }

        return Document(
            title=title,
            content=content,
            metadata=final_metadata
        )
