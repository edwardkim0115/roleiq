from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import AppBaseModel


class GroundedSuggestionDraft(AppBaseModel):
    suggestion_type: Literal["phrasing", "emphasis", "gap", "summary"]
    title: str
    body: str
    grounded: bool
    supporting_fragment_ids: list[str] = Field(default_factory=list)


class GroundedSuggestionPayload(AppBaseModel):
    tailored_summary: str | None = None
    suggestions: list[GroundedSuggestionDraft] = Field(default_factory=list)

