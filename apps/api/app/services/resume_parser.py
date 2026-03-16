from __future__ import annotations

from app.schemas.domain import ResumeProfile, SkillItem, TextFragment
from app.services.heuristics import (
    assign_resume_sections,
    build_raw_sections,
    heuristic_resume_profile,
)
from app.services.normalization import canonicalize_term
from app.services.openai_client import OpenAIService


class ResumeParser:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai_service = openai_service or OpenAIService()

    def parse(self, fragments: list[TextFragment]) -> ResumeProfile:
        sectioned_fragments = assign_resume_sections(fragments)
        heuristic_profile = heuristic_resume_profile(sectioned_fragments)
        raw_sections = build_raw_sections(sectioned_fragments)
        llm_profile = self.openai_service.parse_resume(sectioned_fragments, raw_sections)
        if llm_profile is None:
            return heuristic_profile
        return _sanitize_resume_profile(llm_profile, heuristic_profile)


def _sanitize_resume_profile(profile: ResumeProfile, fallback: ResumeProfile) -> ResumeProfile:
    valid_fragment_ids = {fragment.id for fragment in fallback.text_fragments}

    def keep_ids(values: list[str]) -> list[str]:
        return [value for value in values if value in valid_fragment_ids]

    education = [
        item.model_copy(update={"evidence_fragment_ids": keep_ids(item.evidence_fragment_ids)})
        for item in profile.education
    ]
    experience = [
        item.model_copy(update={"evidence_fragment_ids": keep_ids(item.evidence_fragment_ids)})
        for item in profile.experience
    ]
    projects = [
        item.model_copy(update={"evidence_fragment_ids": keep_ids(item.evidence_fragment_ids)})
        for item in profile.projects
    ]
    skills = [
        SkillItem(
            name=canonicalize_term(item.name) or item.name,
            category=item.category,
            evidence_fragment_ids=keep_ids(item.evidence_fragment_ids),
        )
        for item in profile.skills
    ]

    return ResumeProfile(
        name=profile.name or fallback.name,
        email=profile.email or fallback.email,
        phone=profile.phone or fallback.phone,
        linkedin=profile.linkedin or fallback.linkedin,
        github=profile.github or fallback.github,
        portfolio=profile.portfolio or fallback.portfolio,
        summary=profile.summary or fallback.summary,
        education=[item for item in education if item.school or item.degree] or fallback.education,
        experience=[item for item in experience if item.company or item.title] or fallback.experience,
        projects=[item for item in projects if item.name] or fallback.projects,
        skills=skills or fallback.skills,
        certifications=profile.certifications or fallback.certifications,
        raw_sections=fallback.raw_sections,
        text_fragments=fallback.text_fragments,
    )

