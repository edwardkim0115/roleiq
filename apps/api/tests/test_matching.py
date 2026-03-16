from __future__ import annotations

from app.schemas.domain import JobProfile, RequirementItem
from app.services.matching import MatchEngine
from tests.helpers import sample_resume_profile


def test_requirement_matching_finds_strong_and_missing_matches():
    profile, fragments = sample_resume_profile()
    job = JobProfile(
        title="Backend Engineer",
        company="Example Co",
        location=None,
        job_summary="Backend engineer role",
        responsibilities=[],
        required_skills=["python", "fastapi"],
        preferred_skills=["kubernetes"],
        tools=[],
        domain_keywords=["api"],
        years_experience_required=3,
        education_requirements=[],
        certifications=[],
        seniority=None,
        employment_type=None,
        raw_requirement_items=[
            RequirementItem(
                id="req-python",
                text="Python",
                category="required_skill",
                importance="required",
                normalized_terms=["python"],
            ),
            RequirementItem(
                id="req-fastapi",
                text="FastAPI",
                category="required_skill",
                importance="required",
                normalized_terms=["fastapi"],
            ),
            RequirementItem(
                id="pref-k8s",
                text="Kubernetes",
                category="preferred_skill",
                importance="preferred",
                normalized_terms=["kubernetes"],
            ),
            RequirementItem(
                id="req-years",
                text="3+ years of backend experience",
                category="years_experience",
                importance="required",
                normalized_terms=["backend", "experience"],
                numeric_requirement=3,
            ),
        ],
    )

    evaluations = MatchEngine().evaluate(profile, job, fragments)
    by_id = {evaluation.requirement.id: evaluation for evaluation in evaluations}

    assert by_id["req-python"].match_strength == "strong_match"
    assert set(by_id["req-python"].evidence_fragment_ids) >= {"frag-skills", "frag-exp"}
    assert by_id["pref-k8s"].match_strength == "missing"
    assert by_id["req-years"].match_strength in {"weak_match", "moderate_match"}
