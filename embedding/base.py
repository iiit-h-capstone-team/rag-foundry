"""Base embedding strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class EmbeddingStrategy(BaseStrategy):
    """Base class for embedding strategies.
    
    Defines the interface for embedding implementations.
    """

    @abstractmethod
    def embed(self, texts):
        """Embed text(s) into vector representation(s).
        
        Args:
            texts: String or list of strings to embed.
            
        Returns:
            List of embeddings (vectors).
        """
        pass