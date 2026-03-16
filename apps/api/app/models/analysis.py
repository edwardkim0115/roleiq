from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JSONVariant

if TYPE_CHECKING:
    from app.models.job import JobPosting
    from app.models.resume import ResumeDocument


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    resume_document_id: Mapped[str] = mapped_column(
        ForeignKey("resume_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_posting_id: Mapped[str] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    subscores_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    summary_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    resume_document: Mapped[ResumeDocument] = relationship(back_populates="analyses")
    job_posting: Mapped[JobPosting] = relationship(back_populates="analyses")
    requirement_matches: Mapped[list[RequirementMatch]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    suggestions: Mapped[list[Suggestion]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class RequirementMatch(Base):
    __tablename__ = "requirement_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requirement_id: Mapped[str] = mapped_column(String(64), nullable=False)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    bucket: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    importance: Mapped[str] = mapped_column(String(32), nullable=False)
    match_strength: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    score_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    matched_terms: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    missing_terms: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    evidence_fragment_ids: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="requirement_matches")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suggestion_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    grounded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    supporting_fragment_ids: Mapped[list[str]] = mapped_column(JSONVariant, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="suggestions")
