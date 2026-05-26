from pathlib import Path
from typing import List
import re
import unicodedata

from app.core.config import settings
from app.core.logging import logger
from app.utils.file_parser import load_csv_text, load_pdf_text


class ExtractTransformLoadError(Exception):
    pass


class ETLPipeline:
    def __init__(self):
        self.processed_directory = Path(settings.processed_directory)
        self.processed_directory.mkdir(parents=True, exist_ok=True)

    def extract_text(self, file_path: Path) -> str:
        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                return load_pdf_text(file_path)
            if suffix == ".csv":
                return load_csv_text(file_path)
            raise ExtractTransformLoadError(f"Unsupported file type: {suffix}")
        except Exception as exc:
            logger.exception("Extraction failed for %s", file_path)
            raise ExtractTransformLoadError(f"Extraction failed: {exc}") from exc

    def remove_null_texts(self, texts: List[str]) -> List[str]:
        cleaned_texts = [text for text in texts if text and text.strip()]
        logger.debug("Removed %d null or empty text segments", len(texts) - len(cleaned_texts))
        return cleaned_texts

    def normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text)
        return normalized.strip()

    def clean_text(self, raw_text: str) -> str:
        if raw_text is None:
            raise ExtractTransformLoadError("No text available to clean.")

        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[\x00-\x1f\x7f]+", " ", text).strip()
        text = self.normalize_text(text)

        if not text:
            raise ExtractTransformLoadError("Cleaned text is empty after normalization.")

        return text

    def save_processed_output(self, file_path: Path, text: str) -> Path:
        output_name = file_path.stem + ".txt"
        output_path = self.processed_directory / output_name
        try:
            output_path.write_text(text, encoding="utf-8")
            logger.info("Saved processed output to %s", output_path)
            return output_path
        except Exception as exc:
            logger.exception("Failed to save processed output for %s", file_path)
            raise ExtractTransformLoadError(f"Unable to save processed output: {exc}") from exc

    def run(self, file_path: Path) -> Path:
        try:
            raw_text = self.extract_text(file_path)
            cleaned_text = self.clean_text(raw_text)
            processed_path = self.save_processed_output(file_path, cleaned_text)
            return processed_path
        except ExtractTransformLoadError:
            raise
        except Exception as exc:
            logger.exception("ETL pipeline failed for %s", file_path)
            raise ExtractTransformLoadError(f"ETL pipeline failed: {exc}") from exc
