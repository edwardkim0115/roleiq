from __future__ import annotations

from app.services.document_ingestion import DocumentExtractionError


def test_extract_pdf_preserves_page_metadata(extractor, make_pdf_bytes):
    payload = make_pdf_bytes("Jamie Rivera\nPython Developer")
    extracted = extractor.extract("resume.pdf", payload)

    assert extracted.file_type == "pdf"
    assert extracted.fragments
    assert extracted.fragments[0].page_number == 1
    assert "Jamie Rivera" in extracted.raw_text


def test_extract_docx_preserves_paragraph_order(extractor, make_docx_bytes):
    payload = make_docx_bytes(
        [
            ("Skills", "Heading 1"),
            ("Python, FastAPI, PostgreSQL", None),
            ("Experience", "Heading 1"),
            ("Built APIs for internal tools.", None),
        ]
    )

    extracted = extractor.extract("resume.docx", payload)

    assert extracted.file_type == "docx"
    assert [fragment.text for fragment in extracted.fragments[:3]] == [
        "Skills",
        "Python, FastAPI, PostgreSQL",
        "Experience",
    ]
    assert extracted.fragments[0].section_name == "heading"


def test_extract_txt_splits_paragraphs(extractor):
    payload = b"Summary\nBackend engineer\n\nSkills\nPython, SQL"
    extracted = extractor.extract("resume.txt", payload)

    assert extracted.file_type == "txt"
    assert len(extracted.fragments) == 2
    assert extracted.fragments[0].text.startswith("Summary")


def test_invalid_file_type_is_rejected(extractor):
    try:
        extractor.extract("resume.exe", b"bad")
    except DocumentExtractionError as exc:
        assert "Unsupported file type" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("Expected extraction error")

