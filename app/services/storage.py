from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.services.embeddings import get_embedding_client
from app.core.config import settings
from app.core.logging import logger


class VectorStore:
    def __init__(self):
        self.persist_directory = Path(settings.persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.embedding_client = get_embedding_client()
        self.store = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embedding_client,
            collection_name="ai_rag_documents",
        )

    def add_documents(self, texts: List[str], metadatas: List[dict]):
        documents = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)]
        self.store.add_documents(documents)
        logger.info("Stored %d documents in vector store", len(documents))

    def similarity_search(self, query: str, k: int = 3):
        return self.store.similarity_search(query, k=k)

    def delete_collection(self):
        self.store.delete_collection()
        logger.info("Deleted vector store collection")
