from pathlib import Path
from app.pipeline.etl import ETLPipeline
from app.pipeline.embedding_pipeline import EmbeddingPipeline
from app.core.logging import logger


class UploadService:
    def __init__(self):
        self.etl = ETLPipeline()
        self.embedding_pipeline = EmbeddingPipeline()

    def process_pdf(self, file_path: Path):
        processed_path = self.etl.run(file_path)
        text = processed_path.read_text(encoding="utf-8")
        result = self.embedding_pipeline.ingest_text(text, file_path.name)
        result["processed_path"] = str(processed_path)
        return result

    def process_csv(self, file_path: Path):
        processed_path = self.etl.run(file_path)
        text = processed_path.read_text(encoding="utf-8")
        result = self.embedding_pipeline.ingest_text(text, file_path.name)
        result["processed_path"] = str(processed_path)
        return result
