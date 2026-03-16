from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import AppBaseModel
from app.schemas.domain import JobProfile, MatchStrength, ResumeProfile, TextFragment


class DocumentPreview(AppBaseModel):
    filename: str
    file_type: str
    raw_text: str
    fragments: list[TextFragment]


class ResumeDocumentRead(AppBaseModel):
    id: str
    filename: str
    file_type: str
    raw_text: str
    created_at: datetime


class ResumeFragmentRead(AppBaseModel):
    id: str
    section_name: str
    order_index: int
    text: str
    page_number: int | None = None
    block_index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RequirementMatchRead(AppBaseModel):
    id: str
    requirement_id: str
    requirement_text: str
    bucket: str
    category: str
    importance: str
    match_strength: MatchStrength
    score_contribution: float
    confidence_score: float
    explanation: str
    matched_terms: list[str]
    missing_terms: list[str]
    evidence_fragment_ids: list[str]


class SuggestionRead(AppBaseModel):
    id: str
    suggestion_type: str
    title: str
    body: str
    grounded: bool
    supporting_fragment_ids: list[str]
    created_at: datetime


class SubscoreBucket(AppBaseModel):
    key: str
    label: str
    weight: int
    earned_points: float
    possible_points: float
    normalized_score: float | None = None
    applicable: bool = True
    matched_requirements: int = 0
    total_requirements: int = 0


class AnalysisListItem(AppBaseModel):
    id: str
    title: str
    company: str | None = None
    filename: str
    overall_score: float
    created_at: datetime
    top_strengths: list[str] = Field(default_factory=list)
    top_gaps: list[str] = Field(default_factory=list)


class AnalysisDetail(AppBaseModel):
    id: str
    overall_score: float
    created_at: datetime
    updated_at: datetime
    resume_document: ResumeDocumentRead
    fragments: list[ResumeFragmentRead]
    parsed_resume: ResumeProfile
    job_posting: JobProfile
    subscores: list[SubscoreBucket]
    summary: dict[str, Any]
    requirements: list[RequirementMatchRead]
    suggestions: list[SuggestionRead]


class ScoreRead(AppBaseModel):
    analysis_id: str
    overall_score: float
    subscores: list[SubscoreBucket]
    summary: dict[str, Any]


class JobParseRequest(AppBaseModel):
    job_text: str
