from __future__ import annotations

from app.schemas.domain import JobProfile, RequirementItem
from app.services.heuristics import heuristic_job_profile
from app.services.normalization import canonicalize_term, normalize_terms
from app.services.openai_client import OpenAIService


class JobParser:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai_service = openai_service or OpenAIService()

    def parse(self, job_text: str) -> JobProfile:
        heuristic_profile = heuristic_job_profile(job_text)
        llm_profile = self.openai_service.parse_job(job_text)
        if llm_profile is None:
            return heuristic_profile
        return _sanitize_job_profile(llm_profile, heuristic_profile)


def _sanitize_job_profile(profile: JobProfile, fallback: JobProfile) -> JobProfile:
    requirement_ids: set[str] = set()
    requirements: list[RequirementItem] = []
    for item in profile.raw_requirement_items:
        normalized_terms = normalize_terms(item.normalized_terms or [item.text])
        safe_item = item.model_copy(
            update={
                "normalized_terms": normalized_terms,
                "id": item.id or f"req-{len(requirements) + 1}",
                "text": item.text.strip(),
            }
        )
        if not safe_item.text or safe_item.id in requirement_ids:
            continue
        requirement_ids.add(safe_item.id)
        requirements.append(safe_item)

    required_skills = normalize_terms(profile.required_skills or fallback.required_skills)
    preferred_skills = normalize_terms(profile.preferred_skills or fallback.preferred_skills)
    tools = normalize_terms(profile.tools or required_skills + preferred_skills)
    domain_keywords = normalize_terms(profile.domain_keywords or fallback.domain_keywords)

    return JobProfile(
        title=profile.title or fallback.title,
        company=profile.company or fallback.company,
        location=profile.location or fallback.location,
        job_summary=profile.job_summary or fallback.job_summary,
        responsibilities=profile.responsibilities or fallback.responsibilities,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        tools=tools,
        domain_keywords=domain_keywords,
        years_experience_required=profile.years_experience_required or fallback.years_experience_required,
        education_requirements=profile.education_requirements or fallback.education_requirements,
        certifications=profile.certifications or fallback.certifications,
        seniority=canonicalize_term(profile.seniority or "") or fallback.seniority,
        employment_type=profile.employment_type or fallback.employment_type,
        raw_requirement_items=requirements or fallback.raw_requirement_items,
    )

