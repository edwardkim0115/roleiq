from __future__ import annotations

from collections.abc import Iterable

from app.utils.text import tokenize

SKILL_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "node": "node.js",
    "nodejs": "node.js",
    "postgresql": "postgres",
    "psql": "postgres",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "py": "python",
    "k8s": "kubernetes",
    "reactjs": "react",
    "nextjs": "next.js",
    "ci/cd": "continuous integration",
}

KNOWN_SKILLS = {
    "python",
    "typescript",
    "javascript",
    "react",
    "next.js",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "postgres",
    "mysql",
    "redis",
    "docker",
    "kubernetes",
    "terraform",
    "aws",
    "amazon web services",
    "google cloud platform",
    "azure",
    "graphql",
    "rest",
    "sql",
    "nosql",
    "pandas",
    "numpy",
    "airflow",
    "spark",
    "snowflake",
    "dbt",
    "tableau",
    "power bi",
    "git",
    "ci/cd",
    "machine learning",
    "llm",
    "openai",
    "prompt engineering",
    "java",
    "go",
    "c#",
    "c++",
    "linux",
}


def canonicalize_term(term: str) -> str:
    normalized = " ".join(tokenize(term))
    if not normalized:
        return ""
    return SKILL_ALIASES.get(normalized, normalized)


def normalize_terms(terms: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for term in terms:
        canonical = canonicalize_term(term)
        if canonical and canonical not in seen:
            seen.add(canonical)
            output.append(canonical)
    return output


def extract_known_skills(value: str) -> list[str]:
    normalized_value = canonicalize_term(value)
    discovered: list[str] = []
    if normalized_value in KNOWN_SKILLS:
        return [normalized_value]
    joined = " ".join(tokenize(value))
    for skill in KNOWN_SKILLS:
        if skill in joined:
            discovered.append(skill)
    return normalize_terms(discovered)


def normalized_overlap(left: Iterable[str], right: Iterable[str]) -> list[str]:
    left_set = set(normalize_terms(left))
    right_set = set(normalize_terms(right))
    return sorted(left_set & right_set)


def lexical_overlap_score(requirement_terms: Iterable[str], candidate_text: str) -> float:
    req_tokens = set(normalize_terms(requirement_terms) or tokenize(" ".join(requirement_terms)))
    if not req_tokens:
        return 0.0
    candidate_tokens = set(tokenize(candidate_text))
    if not candidate_tokens:
        return 0.0
    overlap = len(req_tokens & candidate_tokens)
    return round(overlap / len(req_tokens), 4)

