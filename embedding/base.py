"""Base embedding strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class EmbeddingStrategy(BaseStrategy):
    """Base class for embedding strategies.
    
    Defines the interface for embedding implementations.
    """

    @abstractmethod
    def embed(self, texts, is_query=False):
        """Embed text(s) into vector representation(s).
        
        Args:
            texts: String or list of strings to embed.
            is_query: If True, apply query-specific processing
                (e.g. instruction prefix for BGE models, separate
                encoder for MedCPT). Defaults to False (document mode).
            
        Returns:
            List of embeddings (vectors).
        """
        pass