from app.utils.file_parser import chunk_text


def test_chunk_text_creates_overlapping_segments():
    text = "".join([f"word{i} " for i in range(1200)])
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 200 for chunk in chunks)
