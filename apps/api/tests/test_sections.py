from __future__ import annotations

from app.schemas.domain import TextFragment
from app.services.heuristics import assign_resume_sections, heuristic_resume_profile


def test_section_detection_assigns_expected_sections():
    fragments = [
        TextFragment(id="1", section_name="heading", order_index=0, text="Summary", source_type="txt"),
        TextFragment(id="2", section_name="unclassified", order_index=1, text="Backend engineer", source_type="txt"),
        TextFragment(id="3", section_name="heading", order_index=2, text="Skills", source_type="txt"),
        TextFragment(id="4", section_name="unclassified", order_index=3, text="Python, FastAPI", source_type="txt"),
        TextFragment(id="5", section_name="heading", order_index=4, text="Experience", source_type="txt"),
        TextFragment(
            id="6",
            section_name="unclassified",
            order_index=5,
            text="Backend Intern | Acme | Jan 2023 - Dec 2023\nBuilt APIs",
            source_type="txt",
        ),
    ]

    sectioned = assign_resume_sections(fragments)

    assert sectioned[1].section_name == "summary"
    assert sectioned[3].section_name == "skills"
    assert sectioned[5].section_name == "experience"


def test_heuristic_resume_profile_extracts_contact_and_skills():
    fragments = [
        TextFragment(id="1", section_name="unclassified", order_index=0, text="Jamie Rivera", source_type="txt"),
        TextFragment(
            id="2",
            section_name="unclassified",
            order_index=1,
            text="jrivera@example.com",
            source_type="txt",
        ),
        TextFragment(id="3", section_name="heading", order_index=2, text="Skills", source_type="txt"),
        TextFragment(
            id="4",
            section_name="unclassified",
            order_index=3,
            text="Python, FastAPI, PostgreSQL",
            source_type="txt",
        ),
    ]

    profile = heuristic_resume_profile(fragments)

    assert profile.name == "Jamie Rivera"
    assert profile.email == "jrivera@example.com"
    assert {skill.name for skill in profile.skills} >= {"python", "fastapi", "postgres"}

