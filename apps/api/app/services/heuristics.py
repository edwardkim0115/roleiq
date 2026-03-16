from __future__ import annotations

import re
from collections import Counter

from app.schemas.domain import (
    EducationItem,
    ExperienceItem,
    JobProfile,
    ProjectItem,
    RequirementItem,
    ResumeProfile,
    SkillItem,
    TextFragment,
)
from app.services.normalization import canonicalize_term, extract_known_skills, normalize_terms
from app.utils.text import clean_text, sentence_chunks, slugify, split_lines, tokenize

SECTION_HEADINGS = {
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "education": "education",
    "projects": "projects",
    "project experience": "projects",
    "skills": "skills",
    "technical skills": "skills",
    "certifications": "certifications",
    "summary": "summary",
    "professional summary": "summary",
    "profile": "summary",
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?){2}\d{4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[^\s]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[^\s]+", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\+?\s+years?", re.IGNORECASE)
DATE_RANGE_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})[A-Za-z ,]*?)\s*(?:-|to|–)\s*((?:Present|Current|Now|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})[A-Za-z ,]*?)",
    re.IGNORECASE,
)
RESPONSIBILITY_HEADINGS = {"responsibilities", "what you'll do", "what you will do", "what you’ll do"}
REQUIRED_HEADINGS = {"requirements", "qualifications", "must have", "required"}
PREFERRED_HEADINGS = {"preferred", "nice to have", "bonus", "preferred qualifications"}

STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "you",
    "will",
    "this",
    "that",
    "our",
    "your",
    "from",
    "have",
    "are",
    "job",
    "role",
    "team",
    "experience",
}


def assign_resume_sections(fragments: list[TextFragment]) -> list[TextFragment]:
    current_section = "header"
    updated: list[TextFragment] = []
    for fragment in sorted(fragments, key=lambda item: item.order_index):
        candidate = clean_text(fragment.text).strip(":").lower()
        lines = split_lines(fragment.text)
        first_line = lines[0].strip(":").lower() if lines else candidate
        if first_line in SECTION_HEADINGS:
            current_section = SECTION_HEADINGS[first_line]
            updated.append(fragment.model_copy(update={"section_name": current_section}))
            continue
        if candidate in SECTION_HEADINGS or candidate.rstrip(":") in SECTION_HEADINGS:
            current_section = SECTION_HEADINGS[candidate.rstrip(":")]
            updated.append(fragment.model_copy(update={"section_name": current_section}))
            continue

        if fragment.section_name == "heading" and candidate in SECTION_HEADINGS:
            current_section = SECTION_HEADINGS[candidate]
        updated.append(fragment.model_copy(update={"section_name": current_section}))
    return updated


def build_raw_sections(fragments: list[TextFragment]) -> list[dict]:
    sections: list[dict] = []
    grouped: dict[str, list[TextFragment]] = {}
    for fragment in fragments:
        grouped.setdefault(fragment.section_name, []).append(fragment)
    for section_name, items in grouped.items():
        sections.append(
            {
                "name": section_name,
                "fragment_ids": [item.id for item in items],
                "text": "\n\n".join(item.text for item in items),
            }
        )
    return sections


def heuristic_resume_profile(fragments: list[TextFragment]) -> ResumeProfile:
    fragments = assign_resume_sections(fragments)
    full_text = "\n".join(fragment.text for fragment in fragments)
    lines = [line for fragment in fragments for line in split_lines(fragment.text)]
    first_line = lines[0] if lines else None

    summary_fragments = [fragment for fragment in fragments if fragment.section_name == "summary"]
    education_fragments = [fragment for fragment in fragments if fragment.section_name == "education"]
    experience_fragments = [fragment for fragment in fragments if fragment.section_name == "experience"]
    project_fragments = [fragment for fragment in fragments if fragment.section_name == "projects"]
    skill_fragments = [fragment for fragment in fragments if fragment.section_name == "skills"]
    cert_fragments = [fragment for fragment in fragments if fragment.section_name == "certifications"]

    raw_skills: list[SkillItem] = []
    for fragment in skill_fragments:
        for line in split_lines(fragment.text):
            if canonicalize_term(line) == "skills":
                continue
            parts = re.split(r"[|,;/]", line)
            for part in parts:
                for skill in extract_known_skills(part) or [canonicalize_term(part)]:
                    if skill:
                        raw_skills.append(
                            SkillItem(
                                name=skill,
                                category="technical",
                                evidence_fragment_ids=[fragment.id],
                            )
                        )

    education = [_parse_education_fragment(fragment) for fragment in education_fragments]
    experience = [_parse_experience_fragment(fragment) for fragment in experience_fragments]
    projects = [_parse_project_fragment(fragment) for fragment in project_fragments]

    derived_skills = raw_skills + _extract_skills_from_experience_and_projects(experience, projects)
    deduped_skills: dict[str, SkillItem] = {}
    for skill in derived_skills:
        canonical = canonicalize_term(skill.name)
        if not canonical:
            continue
        if canonical in deduped_skills:
            deduped_skills[canonical].evidence_fragment_ids = list(
                dict.fromkeys(deduped_skills[canonical].evidence_fragment_ids + skill.evidence_fragment_ids)
            )
            continue
        deduped_skills[canonical] = skill.model_copy(update={"name": canonical})

    certifications: list[str] = []
    for fragment in cert_fragments:
        certifications.extend(line for line in split_lines(fragment.text) if "certification" not in line.lower())

    return ResumeProfile(
        name=_guess_name(first_line),
        email=_first_match(EMAIL_RE, full_text),
        phone=_first_match(PHONE_RE, full_text),
        linkedin=_first_match(LINKEDIN_RE, full_text),
        github=_first_match(GITHUB_RE, full_text),
        portfolio=_guess_portfolio(full_text),
        summary="\n".join(fragment.text for fragment in summary_fragments) or None,
        education=[item for item in education if item.school or item.degree],
        experience=[item for item in experience if item.company or item.title],
        projects=[item for item in projects if item.name],
        skills=list(deduped_skills.values()),
        certifications=certifications,
        raw_sections=build_raw_sections(fragments),
        text_fragments=fragments,
    )


def heuristic_job_profile(job_text: str) -> JobProfile:
    normalized_text = clean_text(job_text)
    lines = split_lines(normalized_text)
    title = lines[0] if lines else None
    company = lines[1] if len(lines) > 1 and len(lines[1]) < 80 else None
    location = next((line for line in lines[:6] if any(token in line.lower() for token in ["remote", ",", "hybrid"])), None)

    responsibilities: list[str] = []
    required_lines: list[str] = []
    preferred_lines: list[str] = []
    education_requirements: list[str] = []
    certifications: list[str] = []
    current_section = "summary"

    for line in lines[1:]:
        lowered = line.strip(":").lower()
        if lowered in RESPONSIBILITY_HEADINGS:
            current_section = "responsibilities"
            continue
        if lowered in REQUIRED_HEADINGS:
            current_section = "required"
            continue
        if lowered in PREFERRED_HEADINGS:
            current_section = "preferred"
            continue
        if "education" == lowered:
            current_section = "education"
            continue
        if "certification" in lowered:
            current_section = "certifications"
            continue

        if current_section == "responsibilities":
            responsibilities.append(line)
        elif current_section == "required":
            required_lines.append(line)
        elif current_section == "preferred":
            preferred_lines.append(line)
        elif current_section == "education":
            education_requirements.append(line)
        elif current_section == "certifications":
            certifications.append(line)

    job_summary = "\n".join(lines[: min(len(lines), 6)])
    required_skills = normalize_terms(skill for line in required_lines for skill in extract_known_skills(line))
    preferred_skills = normalize_terms(skill for line in preferred_lines for skill in extract_known_skills(line))
    tools = normalize_terms(required_skills + preferred_skills)
    years_match = YEARS_RE.search(normalized_text)
    years_required = float(years_match.group(1)) if years_match else None
    seniority = _detect_seniority(normalized_text)
    employment_type = _detect_employment_type(normalized_text)
    domain_keywords = _top_keywords(job_summary + "\n" + "\n".join(responsibilities + required_lines))

    requirement_items: list[RequirementItem] = []
    for skill in required_skills:
        requirement_items.append(
            RequirementItem(
                id=f"req-{slugify(skill)}",
                text=skill,
                category="required_skill",
                importance="required",
                normalized_terms=[skill],
            )
        )
    for skill in preferred_skills:
        requirement_items.append(
            RequirementItem(
                id=f"pref-{slugify(skill)}",
                text=skill,
                category="preferred_skill",
                importance="preferred",
                normalized_terms=[skill],
            )
        )
    for index, responsibility in enumerate(responsibilities):
        requirement_items.append(
            RequirementItem(
                id=f"resp-{index + 1}",
                text=responsibility,
                category="responsibility",
                importance="required",
                normalized_terms=normalize_terms(extract_known_skills(responsibility) + tokenize(responsibility)[:6]),
            )
        )
    for index, education in enumerate(education_requirements):
        requirement_items.append(
            RequirementItem(
                id=f"edu-{index + 1}",
                text=education,
                category="education",
                importance="required",
                normalized_terms=normalize_terms(tokenize(education)),
            )
        )
    for index, certification in enumerate(certifications):
        requirement_items.append(
            RequirementItem(
                id=f"cert-{index + 1}",
                text=certification,
                category="certification",
                importance="preferred",
                normalized_terms=normalize_terms(tokenize(certification)),
            )
        )
    if years_required is not None:
        requirement_items.append(
            RequirementItem(
                id="years-experience",
                text=f"{years_required:g}+ years of experience",
                category="years_experience",
                importance="required",
                normalized_terms=["experience"],
                numeric_requirement=years_required,
            )
        )
    for index, keyword in enumerate(domain_keywords[:5]):
        requirement_items.append(
            RequirementItem(
                id=f"keyword-{index + 1}",
                text=keyword,
                category="keyword",
                importance="inferred",
                normalized_terms=[keyword],
            )
        )

    return JobProfile(
        title=title,
        company=company,
        location=location,
        job_summary=job_summary,
        responsibilities=responsibilities,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        tools=tools,
        domain_keywords=domain_keywords,
        years_experience_required=years_required,
        education_requirements=education_requirements,
        certifications=certifications,
        seniority=seniority,
        employment_type=employment_type,
        raw_requirement_items=requirement_items,
    )


def _parse_education_fragment(fragment: TextFragment) -> EducationItem:
    lines = split_lines(fragment.text)
    joined = " | ".join(lines)
    school = lines[0] if lines else ""
    degree = next((line for line in lines if any(term in line.lower() for term in ["bachelor", "master", "phd", "b.s", "m.s"])), "")
    field = next((line for line in lines if "computer" in line.lower() or "engineering" in line.lower()), None)
    return EducationItem(
        school=school,
        degree=degree or joined,
        field=field,
        start_date=None,
        end_date=None,
        evidence_fragment_ids=[fragment.id],
    )


def _parse_experience_fragment(fragment: TextFragment) -> ExperienceItem:
    lines = split_lines(fragment.text)
    first_line = lines[0] if lines else ""
    segments = [segment.strip() for segment in re.split(r"\|| @ | at ", first_line) if segment.strip()]
    title = segments[0] if segments else first_line
    company = segments[1] if len(segments) > 1 else ""
    location = segments[2] if len(segments) > 2 else None
    start_date = None
    end_date = None
    date_text = " ".join(lines[:2])
    date_match = DATE_RANGE_RE.search(date_text)
    if date_match:
        start_date = date_match.group(1)
        end_date = date_match.group(2)
    bullets = lines[1:] if len(lines) > 1 else sentence_chunks(fragment.text)[1:]
    technologies = normalize_terms(skill for line in lines for skill in extract_known_skills(line))
    return ExperienceItem(
        company=company,
        title=title,
        location=location,
        start_date=start_date,
        end_date=end_date,
        bullets=bullets,
        technologies=technologies,
        evidence_fragment_ids=[fragment.id],
    )


def _parse_project_fragment(fragment: TextFragment) -> ProjectItem:
    lines = split_lines(fragment.text)
    name = lines[0] if lines else ""
    description = lines[1] if len(lines) > 1 else fragment.text
    bullets = lines[1:] if len(lines) > 1 else sentence_chunks(fragment.text)
    technologies = normalize_terms(skill for line in lines for skill in extract_known_skills(line))
    return ProjectItem(
        name=name,
        description=description,
        bullets=bullets,
        technologies=technologies,
        evidence_fragment_ids=[fragment.id],
    )


def _extract_skills_from_experience_and_projects(
    experience: list[ExperienceItem],
    projects: list[ProjectItem],
) -> list[SkillItem]:
    output: list[SkillItem] = []
    for item in [*experience, *projects]:
        for technology in item.technologies:
            output.append(
                SkillItem(
                    name=technology,
                    category="derived",
                    evidence_fragment_ids=item.evidence_fragment_ids,
                )
            )
    return output


def _guess_name(first_line: str | None) -> str | None:
    if not first_line:
        return None
    if any(char.isdigit() for char in first_line) or "@" in first_line:
        return None
    if len(first_line.split()) > 5:
        return None
    return first_line


def _first_match(pattern: re.Pattern[str], value: str) -> str | None:
    match = pattern.search(value)
    return match.group(0) if match else None


def _guess_portfolio(value: str) -> str | None:
    urls = URL_RE.findall(value)
    for url in urls:
        lowered = url.lower()
        if "linkedin.com" in lowered or "github.com" in lowered:
            continue
        return url
    return None


def _detect_seniority(value: str) -> str | None:
    lowered = value.lower()
    for level in ["intern", "junior", "mid", "senior", "staff", "principal", "lead"]:
        if level in lowered:
            return level
    return None


def _detect_employment_type(value: str) -> str | None:
    lowered = value.lower()
    if "full-time" in lowered or "full time" in lowered:
        return "full-time"
    if "contract" in lowered:
        return "contract"
    if "part-time" in lowered or "part time" in lowered:
        return "part-time"
    return None


def _top_keywords(value: str, limit: int = 8) -> list[str]:
    counts = Counter(token for token in tokenize(value) if token not in STOPWORDS and len(token) > 2)
    return [term for term, _ in counts.most_common(limit)]
