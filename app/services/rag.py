from typing import List

from langchain_openai import ChatOpenAI
from langchain_classic.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate

from app.services.storage import VectorStore
from app.core.config import settings
from app.core.logging import logger


class RAGSystem:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = None
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                temperature=0,
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
                model=settings.openai_model_name,
            )
            logger.info("Configured ChatOpenAI for generative responses")

    def retrieve(self, query: str, k: int = 3):
        return self.vector_store.similarity_search(query, k=k)

    def answer(self, question: str):
        documents = self.retrieve(question)
        if not documents:
            return {"answer": "No documents indexed yet. Upload a PDF or CSV file first.", "sources": []}

        if self.llm:
            prompt = PromptTemplate(
                input_variables=["question", "context"],
                template=(
                    "Use the following context to answer the question. \n"
                    "If the answer is not included in the context, say you do not know.\n\n"
                    "Context:\n{context}\n\nQuestion: {question}\nAnswer:"),
            )
            chain = load_qa_chain(self.llm, chain_type="stuff", prompt=prompt)
            answer = chain.run(input_documents=documents, question=question)
        else:
            answer = (
                "LLM is not configured. Returning retrieved documents for the query.\n\n"
                + "\n\n".join(
                    f"Source: {doc.metadata} \n{doc.page_content}" for doc in documents
                )
            )

        sources = [
            {"metadata": doc.metadata, "content": doc.page_content}
            for doc in documents
        ]
        return {"answer": answer, "sources": sources}
