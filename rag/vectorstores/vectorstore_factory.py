from rag.config.config import VectorStoreConfig
from rag.vectorstores.faiss_store import FaissVectorStore
from rag.config.enums import VectorStoreType


class VectorStoreFactory:
    
    @staticmethod
    def create_vectorstore(
        config: VectorStoreConfig,
        **kwargs
    ):
        strategies = {
            VectorStoreType.FAISS: lambda: FaissVectorStore(
                config=config.config
            )
        }
        return strategies[config.type]()