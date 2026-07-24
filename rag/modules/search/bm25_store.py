"""BM25 sparse index wrapper using rank_bm25."""

import logging
from typing import List, Tuple

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Store:
    """Lightweight BM25 index over a list of text chunks.

    Tokenizes each chunk by whitespace lowercasing and builds a
    BM25Okapi index.  The ``search`` method returns ``(chunk_index, score)``
    tuples ranked by BM25 score.
    """

    def __init__(self, chunks):
        """Build a BM25 index from chunks.

        Args:
            chunks: List of Chunk objects (must have a ``.text`` attribute).
        """
        self.chunks = chunks
        tokenized = [self._tokenize(chunk.text) for chunk in chunks]
        self.index = BM25Okapi(tokenized)
        logger.info("BM25Store built with %d chunks", len(chunks))

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple whitespace tokenizer with lowercasing."""
        return text.lower().split()

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Search the BM25 index.

        Args:
            query: Query string.
            top_k: Number of results to return.

        Returns:
            List of (chunk_index, score) tuples sorted by descending score.
        """
        tokenized_query = self._tokenize(query)
        scores = self.index.get_scores(tokenized_query)

        # Get top_k indices by score (descending)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        # Filter out zero-score results
        return [(idx, score) for idx, score in ranked if score > 0]
