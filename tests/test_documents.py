import zipfile

import pytest

from pa import documents


def test_reference_text_is_included_and_credentials_rejected(tmp_path):
    f = tmp_path / "자료.txt"
    f.write_text("검증한 사실", encoding="utf-8")
    assert "검증한 사실" in documents.context([f])
    secret = tmp_path / ".env"
    secret.write_text("secret", encoding="utf-8")
    with pytest.raises(ValueError):
        documents.extract(secret)


def test_pptx_slides_keep_numeric_order(tmp_path):
    file = tmp_path / "slides.pptx"
    with zipfile.ZipFile(file, "w") as z:
        for n in (10, 2, 1):
            z.writestr(f"ppt/slides/slide{n}.xml", f'<root><t>slide{n}</t></root>')
    text = documents.extract(file)
    assert text.index("slide1") < text.index("slide2") < text.index("slide10")


def test_oversized_context_is_refused_not_silently_truncated(tmp_path, monkeypatch):
    f = tmp_path / "text.txt"
    f.write_text("a" * 50, encoding="utf-8")
    monkeypatch.setattr(documents, "MAX_CHARS", 30)
    with pytest.raises(ValueError):
        documents.context([f])
