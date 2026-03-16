from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JSONVariant, VectorType

if TYPE_CHECKING:
    from app.models.analysis import Analysis


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class ResumeDocument(Base):
    __tablename__ = "resume_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    fragments: Mapped[list[ResumeFragment]] = relationship(
        back_populates="resume_document",
        cascade="all, delete-orphan",
        order_by="ResumeFragment.order_index",
    )
    parsed_resume: Mapped[ParsedResume | None] = relationship(
        back_populates="resume_document",
        cascade="all, delete-orphan",
        uselist=False,
    )
    analyses: Mapped[list[Analysis]] = relationship(back_populates="resume_document")


class ResumeFragment(Base):
    __tablename__ = "resume_fragments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    resume_document_id: Mapped[str] = mapped_column(
        ForeignKey("resume_documents.id", ondelete="CASCADE"),
        index=True,
    )
    section_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    block_index: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(VectorType(1536))
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONVariant, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    resume_document: Mapped[ResumeDocument] = relationship(back_populates="fragments")


class ParsedResume(Base):
    __tablename__ = "parsed_resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    resume_document_id: Mapped[str] = mapped_column(
        ForeignKey("resume_documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    structured_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    resume_document: Mapped[ResumeDocument] = relationship(back_populates="parsed_resume")
