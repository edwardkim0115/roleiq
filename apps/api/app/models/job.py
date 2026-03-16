from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JSONVariant

if TYPE_CHECKING:
    from app.models.analysis import Analysis


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str | None] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_json: Mapped[dict] = mapped_column(JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    analyses: Mapped[list[Analysis]] = relationship(back_populates="job_posting")
