"""Token-based chunking strategy implementation.

Uses an actual tokenizer (tiktoken, HuggingFace, or SentencePiece) to
count and split by sub-word tokens rather than whitespace words.
For simple word-based splitting, use the ``fixed_word`` strategy.
"""

from rag.modules.chunking.base import ChunkingStrategy
from rag.modules.chunking.registry import chunking_registry
from rag.modules.chunking.enums import ChunkingType
from rag.modules.chunking.strategies.token.config import TokenChunkingConfig, TokenizerType
from rag.models.chunk import Chunk
from rag.models.document import Document


@chunking_registry.register(ChunkingType.TOKEN)
class TokenChunkingStrategy(ChunkingStrategy):
    """Chunking strategy based on actual tokenizer token count."""

    def __init__(self, config: TokenChunkingConfig):
        super().__init__(config)
        self._tokenizer = None
        self._tokenizer_type = TokenizerType(config.tokenizer_type)

    @property
    def tokenizer(self):
        """Lazy-load the tokenizer on first use."""
        if self._tokenizer is not None:
            return self._tokenizer

        if self._tokenizer_type == TokenizerType.TIKTOKEN:
            import tiktoken
            if self.config.model_name:
                self._tokenizer = tiktoken.encoding_for_model(self.config.model_name)
            else:
                self._tokenizer = tiktoken.get_encoding(self.config.encoding_name)

        elif self._tokenizer_type == TokenizerType.HUGGINGFACE:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        elif self._tokenizer_type == TokenizerType.SENTENCEPIECE:
            import sentencepiece as spm
            sp = spm.SentencePieceProcessor()
            sp.Load(self.config.model_name)
            self._tokenizer = sp

        else:
            raise ValueError(f"Unsupported tokenizer type: {self._tokenizer_type}")

        return self._tokenizer

    def encode(self, text: str) -> list[int]:
        """Encode text to token IDs."""
        if self._tokenizer_type == TokenizerType.TIKTOKEN:
            return self.tokenizer.encode(text)
        elif self._tokenizer_type == TokenizerType.HUGGINGFACE:
            return self.tokenizer.encode(text, add_special_tokens=False)
        elif self._tokenizer_type == TokenizerType.SENTENCEPIECE:
            return self.tokenizer.Encode(text)
        raise ValueError(f"Unsupported tokenizer type: {self._tokenizer_type}")

    def decode(self, token_ids: list[int]) -> str:
        """Decode token IDs back to text."""
        if self._tokenizer_type == TokenizerType.TIKTOKEN:
            return self.tokenizer.decode(token_ids)
        elif self._tokenizer_type == TokenizerType.HUGGINGFACE:
            return self.tokenizer.decode(token_ids, skip_special_tokens=True)
        elif self._tokenizer_type == TokenizerType.SENTENCEPIECE:
            return self.tokenizer.Decode(token_ids)
        raise ValueError(f"Unsupported tokenizer type: {self._tokenizer_type}")

    @property
    def max_tokens(self) -> int:
        return self.config.max_tokens

    @property
    def overlap_tokens(self) -> int:
        return self.config.overlap_tokens

    def chunk(self, document: Document) -> list[Chunk]:
        token_ids = self.encode(document.content)
        chunks = []
        i = 0

        while i < len(token_ids):
            chunk_ids = token_ids[i : i + self.max_tokens]
            chunk_text = self.decode(chunk_ids).strip()

            if chunk_text:
                chunk = Chunk(
                    text=chunk_text,
                    metadata={
                        **document.metadata,
                        "chunk_type": "token_based",
                        "token_count": len(chunk_ids),
                        "title": document.title,
                    },
                )
                chunks.append(chunk)

            step = self.max_tokens - self.overlap_tokens
            if step <= 0:
                step = 1
            i += step

        return chunks
