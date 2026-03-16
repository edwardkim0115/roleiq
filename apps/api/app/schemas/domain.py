from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import AppBaseModel

SourceType = Literal["pdf", "docx", "txt"]
RequirementCategory = Literal[
    "required_skill",
    "preferred_skill",
    "responsibility",
    "education",
    "certification",
    "years_experience",
    "domain",
    "keyword",
    "other",
]
RequirementImportance = Literal["required", "preferred", "inferred"]
MatchStrength = Literal["strong_match", "moderate_match", "weak_match", "missing"]


class TextFragment(AppBaseModel):
    id: str
    section_name: str
    order_index: int
    text: str
    source_type: SourceType
    page_number: int | None = None
    block_index: int | None = None
    char_start: int | None = None
    char_end: int | None = None


class EducationItem(AppBaseModel):
    school: str
    degree: str
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    honors: str | None = None
    evidence_fragment_ids: list[str] = Field(default_factory=list)


class ExperienceItem(AppBaseModel):
    company: str
    title: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    evidence_fragment_ids: list[str] = Field(default_factory=list)


class ProjectItem(AppBaseModel):
    name: str
    description: str
    bullets: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    evidence_fragment_ids: list[str] = Field(default_factory=list)


class SkillItem(AppBaseModel):
    name: str
    category: str | None = None
    evidence_fragment_ids: list[str] = Field(default_factory=list)


class ResumeProfile(AppBaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    summary: str | None = None
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills: list[SkillItem] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    raw_sections: list[dict] = Field(default_factory=list)
    text_fragments: list[TextFragment] = Field(default_factory=list)


class RequirementItem(AppBaseModel):
    id: str
    text: str
    category: RequirementCategory
    importance: RequirementImportance
    normalized_terms: list[str] = Field(default_factory=list)
    numeric_requirement: float | None = None


class JobProfile(AppBaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    job_summary: str
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
    years_experience_required: float | None = None
    education_requirements: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    seniority: str | None = None
    employment_type: str | None = None
    raw_requirement_items: list[RequirementItem] = Field(default_factory=list)

