import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

class Settings:
    project_name: str = "AI RAG Data Pipeline"
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    persist_directory: Path = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", BASE_DIR / "data" / "vector_db"))
    processed_directory: Path = Path(os.getenv("PROCESSED_DATA_DIRECTORY", BASE_DIR / "data" / "processed_data"))
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    _api_key = os.getenv("OPENAI_API_KEY")
    openai_api_key: str | None = _api_key.strip() if (_api_key and _api_key.strip() and "your_api_key" not in _api_key) else None
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "https://models.github.ai/inference")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "github/embeddings-similarity-text-0.1")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "openai/gpt-4o")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

settings = Settings()
