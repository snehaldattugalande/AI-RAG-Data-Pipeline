from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory

from app.services.storage import VectorStore
from app.core.config import settings
from app.core.logging import logger


class ChatServiceError(Exception):
    pass


class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.memory_store: Dict[str, ConversationBufferMemory] = {}
        self.llm = self._get_llm()

    def _get_llm(self):
        if not settings.openai_api_key:
            message = "OpenAI API key is required for chat LLM generation."
            logger.error(message)
            raise ChatServiceError(message)

        try:
            return ChatOpenAI(
                temperature=0,
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
                model=settings.openai_model_name,
            )
        except Exception as exc:
            logger.exception("Failed to instantiate ChatOpenAI")
            raise ChatServiceError("Unable to initialize chat LLM") from exc

    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        if session_id not in self.memory_store:
            self.memory_store[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
            )
            logger.info("Created new chat memory for session %s", session_id)
        return self.memory_store[session_id]

    def get_retriever(self, k: int = 3):
        try:
            return self.vector_store.store.as_retriever(search_kwargs={"k": k})
        except Exception as exc:
            logger.exception("Failed to build retriever from vector store")
            raise ChatServiceError("Unable to initialize retriever") from exc

    def create_chain(self, session_id: str):
        retriever = self.get_retriever()
        memory = self.get_memory(session_id)
        try:
            return ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                output_key="answer",
                verbose=False,
            )
        except Exception as exc:
            logger.exception("Failed to instantiate conversational retrieval chain")
            raise ChatServiceError("Unable to create chat chain") from exc

    def chat(self, question: str, session_id: str = "default") -> dict:
        if not question or not question.strip():
            raise ChatServiceError("Question cannot be empty.")

        chain = self.create_chain(session_id)
        try:
            response = chain({"question": question})
            logger.info("Chat query executed for session %s", session_id)
            return response
        except Exception as exc:
            logger.exception("Chat query failed for session %s", session_id)
            raise ChatServiceError("Chat query failed") from exc

    def reset_session(self, session_id: str) -> None:
        if session_id in self.memory_store:
            del self.memory_store[session_id]
            logger.info("Cleared chat memory for session %s", session_id)
