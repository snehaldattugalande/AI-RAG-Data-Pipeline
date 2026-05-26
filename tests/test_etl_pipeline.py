import pytest
from app.pipeline.etl import ETLPipeline, ExtractTransformLoadError

def test_etl_clean_text_normalizes_whitespace():
    pipeline = ETLPipeline()
    raw = "Hello   \n\r  world!\tThis is   a test.  "
    clean = pipeline.clean_text(raw)
    assert clean == "Hello world! This is a test."

def test_etl_clean_text_fails_on_none_or_empty():
    pipeline = ETLPipeline()
    with pytest.raises(ExtractTransformLoadError):
        pipeline.clean_text("")
    with pytest.raises(ExtractTransformLoadError):
        pipeline.clean_text(None)

def test_etl_remove_null_texts():
    pipeline = ETLPipeline()
    texts = ["hello", "", "   ", "world", "\n"]
    cleaned = pipeline.remove_null_texts(texts)
    assert cleaned == ["hello", "world"]

def test_etl_normalize_text():
    pipeline = ETLPipeline()
    raw = "H\u00e9llo" # 'é' with accent
    normalized = pipeline.normalize_text(raw)
    assert normalized == "H\u00e9llo"
