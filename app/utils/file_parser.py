from pathlib import Path
from typing import List

import pandas as pd
from PyPDF2 import PdfReader

from app.core.config import settings


def load_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def load_csv_text(file_path: Path) -> str:
    df = pd.read_csv(file_path)
    if df.empty:
        return ""

    df = df.dropna(how="all")
    df = df.fillna("")
    rows: List[str] = []
    for _, row in df.iterrows():
        row_items = []
        for column in df.columns:
            cell = row[column]
            if pd.isna(cell):
                continue
            value = str(cell).strip()
            if value:
                row_items.append(f"{column}: {value}")

        if row_items:
            rows.append(" | ".join(row_items))
    return "\n".join(rows)


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> List[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    tokens = text.split()
    if not tokens:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
