from dataclasses import dataclass
from typing import Dict, Any

from rag.models.document import Document

@dataclass
class QueryResult:
    query: str
    retrieved_docs: list[Document]
    answer: str
    metadata: Dict[str, Any]