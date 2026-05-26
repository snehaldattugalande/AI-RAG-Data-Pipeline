import requests

from app.core.config import settings
from app.core.logging import logger
from langchain_core.embeddings import Embeddings


class GitHubInferenceEmbeddings(Embeddings):
    def __init__(self, model: str, api_base: str, api_key: str):
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request_embeddings(self, inputs):
        response = requests.post(
            f"{self.api_base}/embeddings",
            headers=self.headers,
            json={"model": self.model, "input": inputs},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return [item["embedding"] for item in payload["data"]]

    def embed_documents(self, texts):
        return self._request_embeddings(texts)

    def embed_query(self, text):
        return self._request_embeddings([text])[0]


def get_embedding_client():
    if not settings.openai_api_key:
        logger.error("GitHub embedding model requires OPENAI_API_KEY to be set.")
        raise RuntimeError(
            "OPENAI_API_KEY is required for GitHub embeddings. "
            "Set OPENAI_API_KEY to your GitHub PAT and OPENAI_API_BASE to https://models.github.ai/inference."
        )

    logger.info(
        "Using GitHub embeddings model %s via %s",
        settings.embedding_model_name,
        settings.openai_api_base,
    )

    if settings.openai_api_base and "models.github.ai/inference" in settings.openai_api_base:
        return GitHubInferenceEmbeddings(
            model=settings.embedding_model_name,
            api_base=settings.openai_api_base,
            api_key=settings.openai_api_key,
        )

    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        logger.error("OpenAIEmbeddings requires `langchain_openai`: %s", exc)
        raise

    return OpenAIEmbeddings(
        model=settings.embedding_model_name,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        check_embedding_ctx_length=False,
        encoding_format="float",
    )
