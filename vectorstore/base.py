"""Base vector store strategy class."""

from abc import abstractmethod

from core.strategy import BaseStrategy


class VectorStoreStrategy(BaseStrategy):
    """Base class for vector store strategies."""

    @abstractmethod
    def add(self, embeddings, chunks):
        """Add embeddings and chunks to the vector store.
        
        Args:
            embeddings: Array of embeddings.
            chunks: List of chunk objects.
        """
        pass

    @abstractmethod
    def search(self, query_embedding, top_k):
        """Search for nearest neighbors.
        
        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.
            
        Returns:
            Tuple of (distances, indices).
        """
        pass
