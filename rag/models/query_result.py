import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from rag.models.document import Document

@dataclass
class QueryResult:
    query: str
    retrieved_docs: list[Document]
    answer: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert QueryResult to JSON-serializable dictionary."""
        # Convert retrieved_docs (list of Document objects) to dicts
        retrieved_docs_dict = [
            {
                "title": doc.title,
                "content": doc.content,
                "metadata": doc.metadata
            }
            for doc in self.retrieved_docs
        ]
        
        return {
            "query": self.query,
            "retrieved_docs": retrieved_docs_dict,
            "answer": self.answer,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryResult':
        """Reconstruct QueryResult from dictionary."""
        # Convert retrieved_docs back to Document objects
        retrieved_docs = [
            Document(
                title=doc["title"],
                content=doc["content"],
                metadata=doc.get("metadata", {})
            )
            for doc in data["retrieved_docs"]
        ]
        
        return cls(
            query=data["query"],
            retrieved_docs=retrieved_docs,
            answer=data["answer"],
            metadata=data.get("metadata", {})
        )