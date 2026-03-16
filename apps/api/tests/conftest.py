from __future__ import annotations

from io import BytesIO

import fitz
import pytest
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.services.document_ingestion import DocumentExtractor


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine) -> Session:
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def override_db():
        session = testing_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def extractor() -> DocumentExtractor:
    return DocumentExtractor(max_size_bytes=5 * 1024 * 1024)


@pytest.fixture
def make_pdf_bytes():
    def _make_pdf_bytes(text: str) -> bytes:
        document = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), text)
        payload = document.tobytes()
        document.close()
        return payload

    return _make_pdf_bytes


@pytest.fixture
def make_docx_bytes():
    def _make_docx_bytes(paragraphs: list[tuple[str, str | None]]) -> bytes:
        document = Document()
        for text, style in paragraphs:
            paragraph = document.add_paragraph(text)
            if style:
                paragraph.style = style
        buffer = BytesIO()
        document.save(buffer)
        return buffer.getvalue()

    return _make_docx_bytes
