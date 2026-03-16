from __future__ import annotations

from app.services.normalization import canonicalize_term, extract_known_skills, normalize_terms


def test_skill_aliases_are_normalized():
    assert canonicalize_term("JS") == "javascript"
    assert canonicalize_term("PostgreSQL") == "postgres"
    assert normalize_terms(["js", "javascript", "Node"]) == ["javascript", "node.js"]


def test_extract_known_skills_finds_multiple_terms():
    sentence = "Built Python services with FastAPI and PostgreSQL on AWS."

    assert set(extract_known_skills(sentence)) >= {"python", "fastapi", "postgres", "amazon web services"}

