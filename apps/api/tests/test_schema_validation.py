from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.domain import JobProfile, RequirementItem, ResumeProfile


def test_resume_profile_validation_accepts_minimal_payload():
    payload = ResumeProfile.model_validate(
        {
            "education": [],
            "experience": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "raw_sections": [],
            "text_fragments": [],
        }
    )

    assert payload.skills == []
    assert payload.text_fragments == []


def test_requirement_item_rejects_invalid_category():
    with pytest.raises(ValidationError):
        RequirementItem.model_validate(
            {
                "id": "req-1",
                "text": "Python",
                "category": "made_up",
                "importance": "required",
                "normalized_terms": ["python"],
            }
        )


def test_job_profile_requires_summary():
    with pytest.raises(ValidationError):
        JobProfile.model_validate({"required_skills": []})

