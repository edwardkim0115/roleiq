from __future__ import annotations

from app.models.resume import ResumeFragment
from app.schemas.domain import (
    ExperienceItem,
    RequirementItem,
    ResumeProfile,
    SkillItem,
    TextFragment,
)
from app.services.matching import RequirementEvaluation


def sample_resume_profile() -> tuple[ResumeProfile, list[ResumeFragment]]:
    profile = ResumeProfile(
        name="Jamie Rivera",
        email="jrivera@example.com",
        phone=None,
        linkedin=None,
        github=None,
        portfolio=None,
        summary="Backend engineer with Python API experience.",
        education=[],
        experience=[
            ExperienceItem(
                company="Acme Corp",
                title="Backend Intern",
                location=None,
                start_date="Jan 2023",
                end_date="Dec 2023",
                bullets=[
                    "Built FastAPI services in Python and PostgreSQL.",
                    "Deployed internal tools on AWS.",
                ],
                technologies=["python", "fastapi", "postgres", "amazon web services"],
                evidence_fragment_ids=["frag-exp"],
            )
        ],
        projects=[],
        skills=[
            SkillItem(name="python", category="technical", evidence_fragment_ids=["frag-skills"]),
            SkillItem(name="fastapi", category="technical", evidence_fragment_ids=["frag-skills"]),
            SkillItem(name="postgres", category="technical", evidence_fragment_ids=["frag-skills"]),
        ],
        certifications=[],
        raw_sections=[],
        text_fragments=[
            TextFragment(
                id="frag-skills",
                section_name="skills",
                order_index=0,
                text="Python, FastAPI, PostgreSQL",
                source_type="txt",
            ),
            TextFragment(
                id="frag-exp",
                section_name="experience",
                order_index=1,
                text="Built FastAPI services in Python and PostgreSQL. Deployed internal tools on AWS.",
                source_type="txt",
            ),
        ],
    )

    fragments = [
        ResumeFragment(
            id="frag-skills",
            resume_document_id="resume-1",
            section_name="skills",
            order_index=0,
            text="Python, FastAPI, PostgreSQL",
            metadata_json={"source_type": "txt"},
        ),
        ResumeFragment(
            id="frag-exp",
            resume_document_id="resume-1",
            section_name="experience",
            order_index=1,
            text="Built FastAPI services in Python and PostgreSQL. Deployed internal tools on AWS.",
            metadata_json={"source_type": "txt"},
        ),
    ]
    return profile, fragments


def sample_evaluations() -> list[RequirementEvaluation]:
    return [
        RequirementEvaluation(
            requirement=RequirementItem(
                id="python",
                text="Python",
                category="required_skill",
                importance="required",
                normalized_terms=["python"],
            ),
            bucket="required_skills",
            confidence_score=0.95,
            match_strength="strong_match",
            explanation="matched",
            evidence_fragment_ids=["frag-skills", "frag-exp"],
            matched_terms=["python"],
            missing_terms=[],
        ),
        RequirementEvaluation(
            requirement=RequirementItem(
                id="kubernetes",
                text="Kubernetes",
                category="preferred_skill",
                importance="preferred",
                normalized_terms=["kubernetes"],
            ),
            bucket="preferred_skills",
            confidence_score=0.0,
            match_strength="missing",
            explanation="missing",
            evidence_fragment_ids=[],
            matched_terms=[],
            missing_terms=["kubernetes"],
        ),
    ]


def sample_fragment_lookup() -> dict[str, str]:
    return {
        "frag-skills": "Python, FastAPI, PostgreSQL",
        "frag-exp": "Built FastAPI services in Python and PostgreSQL.",
    }


def sample_resume_text() -> str:
    return """Jamie Rivera
jrivera@example.com

Summary
Backend engineer with Python and API experience.

Skills
Python, FastAPI, PostgreSQL, AWS

Experience
Backend Intern | Acme Corp | Jan 2023 - Dec 2023
- Built FastAPI services in Python and PostgreSQL.
- Deployed internal tools on AWS.

Projects
Inventory API
- Built a Redis-backed API with Docker.

Education
State University
B.S. Computer Science
"""
