"""Title/Passage combined parser implementation.

Unlike the ``title_passage`` parser which stores the title only in
``document.title`` (metadata), this parser concatenates the title into
``document.content`` so that it is embedded, retrieved, and included
in the LLM generation context.
"""

import re
from dataclasses import dataclass
from typing import Dict, Any, Optional

from parsers.base import ParsingStrategy
from parsers.registry import parser_registry
from parsers.enums import ParserType


@dataclass
class TitlePassageCombinedConfig:
    """Configuration for the title/passage combined parser.

    Attributes:
        include_labels: If True, content is formatted as
            ``Title: <title>\nPassage: <passage>``.
            If False (default), content is ``<title>\n\n<passage>``
            which keeps embeddings free of noise tokens.
    """
    include_labels: bool = False


@parser_registry.register(ParserType.TITLE_PASSAGE_COMBINED)
class TitlePassageCombinedParser(ParsingStrategy):
    """Parser that merges title into document content.

    Expected raw format:
        Title: <title text>
        Passage: <passage text>

    Produces a Document where ``content`` is ``<title>\\n\\n<passage>``
    so that the title is embedded and visible to the LLM.
    """

    def __init__(self, config: TitlePassageCombinedConfig = None):
        super().__init__(config)
        if config is None:
            config = TitlePassageCombinedConfig()
        elif isinstance(config, dict):
            config = TitlePassageCombinedConfig(**config)
        self.config = config

    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Parse a document with Title and Passage format, combining both into content."""
        if not raw_document:
            raise ValueError("raw_document cannot be None or empty")

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

        passage = (
            passage_match.group(1).strip()
            if passage_match else raw_document.strip()
        )

        # Combine title and passage into content.
        # When include_labels is True the literal "Title:" / "Passage:"
        # prefixes are kept; otherwise only the raw text is concatenated
        # so that embedding models see only semantically relevant tokens.
        if title:
            if self.config.include_labels:
                content = f"Title: {title}\nPassage: {passage}"
            else:
                content = f"{title}\n\n{passage}"
        else:
            content = passage

        # Merge provided metadata with extracted info
        final_metadata = metadata or {}
        final_metadata = {
            **final_metadata,
            'parser_type': 'title_passage_combined'
        }

        return Document(
            title=title,
            content=content,
            metadata=final_metadata
        )
