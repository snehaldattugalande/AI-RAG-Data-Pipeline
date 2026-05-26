import os

import requests
import streamlit as st

BACKEND_BASE = os.environ.get("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api"
UPLOAD_PDF_ENDPOINT = f"{BACKEND_BASE}{API_PREFIX}/upload/pdf"
UPLOAD_CSV_ENDPOINT = f"{BACKEND_BASE}{API_PREFIX}/upload/csv"
CHAT_ENDPOINT = f"{BACKEND_BASE}{API_PREFIX}/chat"


def show_api_error(response: requests.Response, label: str) -> None:
    st.error(label)
    try:
        payload = response.json()
    except ValueError:
        st.write(response.text)
        return

    detail = payload.get("detail") if isinstance(payload, dict) else payload
    if detail:
        st.warning(detail)
    else:
        st.json(payload)


def post_to_api(*args, **kwargs) -> requests.Response | None:
    try:
        return requests.post(*args, **kwargs)
    except requests.RequestException as exc:
        st.error("Could not reach the backend API.")
        st.warning(str(exc))
        return None


st.set_page_config(
    page_title="AI RAG Data Pipeline",
    layout="wide",
    page_icon="AI",
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.title("AI RAG Pipeline")
page = st.sidebar.selectbox("Navigation", ["Upload", "Chat", "About"])
st.sidebar.markdown("---")
st.sidebar.write("Backend URL")
st.sidebar.code(BACKEND_BASE)

if page == "Upload":
    st.title("Upload Documents")
    st.write("Upload PDF or CSV documents to extract text, create embeddings, and store them in ChromaDB.")

    uploaded_file = st.file_uploader("Choose a PDF or CSV file", type=["pdf", "csv"])
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_bytes = uploaded_file.getvalue()
        file_type = uploaded_file.name.lower()
        endpoint = UPLOAD_PDF_ENDPOINT if file_type.endswith(".pdf") else UPLOAD_CSV_ENDPOINT

        if st.button("Upload and Index"):
            with st.spinner("Uploading and indexing document..."):
                files = {"file": (file_name, file_bytes, uploaded_file.type)}
                response = post_to_api(endpoint, files=files, timeout=120)
                if response is None:
                    st.stop()

                if response.ok:
                    st.success("Document indexed successfully.")
                    st.json(response.json())
                else:
                    show_api_error(response, "Upload failed.")

    st.markdown("---")
    st.info("Supported types: PDF and CSV. Uploading a file will process it and create embeddings for RAG retrieval.")

elif page == "Chat":
    st.title("AI Assistant")
    st.write("Ask questions about your uploaded documents and view the retrieved document chunks.")

    question = st.text_input("Enter your question", key="question_input")
    session_id = st.text_input("Session ID", value="default", help="Use the same session ID to preserve chat context.")

    if st.button("Ask Assistant"):
        if not question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            with st.spinner("Contacting AI assistant..."):
                payload = {"question": question, "session_id": session_id}
                response = post_to_api(CHAT_ENDPOINT, json=payload, timeout=120)
                if response is None:
                    st.stop()

                if response.ok:
                    result = response.json()
                    st.session_state.chat_history.append((question, result.get("answer", "")))
                    st.success("Response received")
                    st.subheader("Answer")
                    st.write(result.get("answer", ""))

                    sources = result.get("sources", [])
                    if sources:
                        st.subheader("Retrieved Document Chunks")
                        for idx, source in enumerate(sources, start=1):
                            metadata = source.get("metadata", {})
                            content = source.get("content", "")
                            with st.expander(f"Chunk {idx} - {metadata.get('source', 'unknown')}"):
                                st.write(content)
                                if metadata:
                                    st.markdown(f"**Metadata:** {metadata}")
                    else:
                        st.info("No source documents were returned for this query.")
                else:
                    show_api_error(response, "Chat query failed.")

    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("Conversation")
        for q, a in reversed(st.session_state.chat_history[-10:]):
            st.markdown(f"**Q:** {q}")
            st.markdown(f"**A:** {a}")

elif page == "About":
    st.title("About this App")
    st.markdown(
        """
        This Streamlit frontend connects to the AI RAG Data Pipeline backend.

        - Upload PDF and CSV files
        - Create embeddings and store them in ChromaDB
        - Ask questions using a conversational RAG assistant
        - View retrieved chunks and metadata
        """
    )
    st.info("Run the backend with `uvicorn main:app --reload` and set BACKEND_URL if needed.")
