from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.resume import ResumeFragment
from app.schemas.domain import JobProfile, RequirementItem, ResumeProfile
from app.services.embeddings import cosine_similarity
from app.services.normalization import canonicalize_term, lexical_overlap_score, normalize_terms
from app.utils.dates import years_from_ranges
from app.utils.text import tokenize

BUCKET_SPECS = {
    "required_skills": {"label": "Required skills / tools coverage", "weight": 30},
    "experience_alignment": {"label": "Experience alignment", "weight": 25},
    "preferred_skills": {"label": "Preferred skills / nice-to-haves", "weight": 15},
    "project_impact": {"label": "Project / impact relevance", "weight": 15},
    "education": {"label": "Education / certifications / qualifications", "weight": 10},
    "keyword_alignment": {"label": "Keyword / terminology alignment", "weight": 5},
}

IMPACT_TERMS = {
    "lead",
    "owned",
    "own",
    "delivered",
    "delivery",
    "launched",
    "launch",
    "improved",
    "optimize",
    "optimized",
    "scaled",
    "scale",
    "performance",
    "architecture",
}


@dataclass
class ResumeIndex:
    fragment_lookup: dict[str, ResumeFragment]
    fragment_tokens: dict[str, set[str]]
    term_locations: dict[str, set[str]]
    skill_terms: set[str]
    skill_section_ids: set[str]
    experience_fragment_ids: set[str]
    project_fragment_ids: set[str]
    education_fragment_ids: set[str]
    certification_fragment_ids: set[str]


@dataclass
class RequirementEvaluation:
    requirement: RequirementItem
    bucket: str
    confidence_score: float
    match_strength: str
    explanation: str
    evidence_fragment_ids: list[str] = field(default_factory=list)
    matched_terms: list[str] = field(default_factory=list)
    missing_terms: list[str] = field(default_factory=list)
    score_contribution: float = 0.0


class MatchEngine:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session

    def evaluate(
        self,
        resume_profile: ResumeProfile,
        job_profile: JobProfile,
        fragments: list[ResumeFragment],
        requirement_embeddings: dict[str, list[float]] | None = None,
    ) -> list[RequirementEvaluation]:
        index = build_resume_index(resume_profile, fragments)
        evaluations: list[RequirementEvaluation] = []
        requirement_embeddings = requirement_embeddings or {}
        for requirement in job_profile.raw_requirement_items:
            requirement_embedding = requirement_embeddings.get(requirement.text)
            evaluations.append(
                self._evaluate_requirement(
                    requirement=requirement,
                    resume_profile=resume_profile,
                    fragments=fragments,
                    index=index,
                    requirement_embedding=requirement_embedding,
                    resume_document_id=fragments[0].resume_document_id if fragments else None,
                )
            )
        return evaluations

    def _evaluate_requirement(
        self,
        requirement: RequirementItem,
        resume_profile: ResumeProfile,
        fragments: list[ResumeFragment],
        index: ResumeIndex,
        requirement_embedding: list[float] | None,
        resume_document_id: str | None,
    ) -> RequirementEvaluation:
        bucket = bucket_for_requirement(requirement)
        term_candidates = normalize_terms(requirement.normalized_terms or tokenize(requirement.text))
        exact_matches = sorted(set(term_candidates) & set(index.term_locations))
        exact_fragment_ids = {
            fragment_id for term in exact_matches for fragment_id in index.term_locations.get(term, set())
        }

        lexical_scores = {
            fragment.id: lexical_overlap_score(term_candidates or tokenize(requirement.text), fragment.text)
            for fragment in fragments
        }
        fts_scores = self._postgres_fts_scores(resume_document_id, requirement.text)
        semantic_scores = {
            fragment.id: cosine_similarity(requirement_embedding, fragment.embedding)
            for fragment in fragments
            if requirement_embedding and fragment.embedding
        }

        if requirement.category == "years_experience":
            return self._evaluate_years_requirement(requirement, resume_profile, bucket)
        if requirement.category in {"education", "certification"}:
            return self._evaluate_qualification_requirement(
                requirement,
                index,
                lexical_scores,
                semantic_scores,
                exact_matches,
                exact_fragment_ids,
                bucket,
            )

        score, evidence_ids, matched_terms, caveat = aggregate_signal_scores(
            requirement=requirement,
            bucket=bucket,
            exact_matches=exact_matches,
            exact_fragment_ids=exact_fragment_ids,
            lexical_scores=lexical_scores,
            fts_scores=fts_scores,
            semantic_scores=semantic_scores,
            index=index,
        )

        strength = strength_from_score(score)
        missing_terms = [term for term in term_candidates if term not in matched_terms]
        explanation = build_explanation(
            requirement=requirement,
            strength=strength,
            score=score,
            evidence_ids=evidence_ids,
            fragments=index.fragment_lookup,
            caveat=caveat,
            matched_terms=matched_terms,
        )
        return RequirementEvaluation(
            requirement=requirement,
            bucket=bucket,
            confidence_score=round(score, 4),
            match_strength=strength,
            explanation=explanation,
            evidence_fragment_ids=evidence_ids,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        )

    def _evaluate_years_requirement(
        self,
        requirement: RequirementItem,
        resume_profile: ResumeProfile,
        bucket: str,
    ) -> RequirementEvaluation:
        supporting_terms = [
            term
            for term in normalize_terms(requirement.normalized_terms + tokenize(requirement.text))
            if term != "experience"
        ]
        relevant_ranges = []
        evidence_ids: list[str] = []
        matched_terms: list[str] = []
        for experience in resume_profile.experience:
            text = " ".join([experience.title, experience.company, *experience.bullets, *experience.technologies])
            text_terms = set(normalize_terms(experience.technologies + tokenize(text)))
            if not supporting_terms or text_terms & set(supporting_terms):
                relevant_ranges.append((experience.start_date, experience.end_date))
                evidence_ids.extend(experience.evidence_fragment_ids)
                matched_terms.extend(sorted(text_terms & set(supporting_terms)))
        if not relevant_ranges:
            relevant_ranges = [(item.start_date, item.end_date) for item in resume_profile.experience]
            evidence_ids = [fragment_id for item in resume_profile.experience for fragment_id in item.evidence_fragment_ids]
        years = years_from_ranges(relevant_ranges)
        required_years = requirement.numeric_requirement or 0.0
        score = min(years / required_years, 1.0) if required_years > 0 else 0.0
        if years == 0 and evidence_ids:
            score = 0.35
        if years == 0 and not evidence_ids:
            strength = "missing"
            explanation = "The resume does not provide dated experience that clearly supports this years-of-experience requirement."
        else:
            strength = strength_from_score(score)
            explanation = (
                f"The resume shows about {years:g} years of relevant dated experience against a stated requirement of "
                f"{required_years:g} years."
            )
            if score < 0.75:
                explanation += " The requirement is only partially supported."
        return RequirementEvaluation(
            requirement=requirement,
            bucket=bucket,
            confidence_score=round(score, 4),
            match_strength=strength,
            explanation=explanation,
            evidence_fragment_ids=list(dict.fromkeys(evidence_ids))[:3],
            matched_terms=sorted(set(matched_terms)) or ["experience"],
            missing_terms=[] if score >= 1.0 else [f"{required_years:g}+ years"],
        )

    def _evaluate_qualification_requirement(
        self,
        requirement: RequirementItem,
        index: ResumeIndex,
        lexical_scores: dict[str, float],
        semantic_scores: dict[str, float],
        exact_matches: list[str],
        exact_fragment_ids: set[str],
        bucket: str,
    ) -> RequirementEvaluation:
        eligible_ids = (
            index.education_fragment_ids
            if requirement.category == "education"
            else index.certification_fragment_ids
        )
        candidate_scores = {
            fragment_id: lexical_scores.get(fragment_id, 0.0)
            for fragment_id in eligible_ids
        }
        if semantic_scores:
            for fragment_id, score in semantic_scores.items():
                if fragment_id in eligible_ids:
                    candidate_scores[fragment_id] = max(candidate_scores.get(fragment_id, 0.0), score)

        evidence_ids = sorted(
            candidate_scores,
            key=lambda fragment_id: candidate_scores[fragment_id],
            reverse=True,
        )[:3]
        best_score = candidate_scores[evidence_ids[0]] if evidence_ids else 0.0
        exact_bonus = 0.65 if exact_matches or exact_fragment_ids else 0.0
        score = min(exact_bonus + (best_score * 0.35), 1.0)
        strength = strength_from_score(score)
        matched_terms = exact_matches
        missing_terms = [
            term for term in normalize_terms(requirement.normalized_terms or tokenize(requirement.text))
            if term not in matched_terms
        ]
        explanation = build_explanation(
            requirement=requirement,
            strength=strength,
            score=score,
            evidence_ids=evidence_ids,
            fragments=index.fragment_lookup,
            caveat=None,
            matched_terms=matched_terms,
        )
        return RequirementEvaluation(
            requirement=requirement,
            bucket=bucket,
            confidence_score=round(score, 4),
            match_strength=strength,
            explanation=explanation,
            evidence_fragment_ids=evidence_ids,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        )

    def _postgres_fts_scores(self, resume_document_id: str | None, requirement_text: str) -> dict[str, float]:
        if not self.session or not self.session.bind or self.session.bind.dialect.name != "postgresql":
            return {}
        if not resume_document_id:
            return {}
        tsvector = func.to_tsvector("english", ResumeFragment.text)
        tsquery = func.plainto_tsquery("english", requirement_text)
        statement = (
            select(
                ResumeFragment.id,
                func.ts_rank_cd(tsvector, tsquery).label("rank"),
            )
            .where(ResumeFragment.resume_document_id == resume_document_id)
            .where(tsvector.op("@@")(tsquery))
            .order_by(desc("rank"))
            .limit(5)
        )
        try:
            rows = self.session.execute(statement).all()
        except SQLAlchemyError:
            return {}
        return {row.id: float(row.rank or 0.0) for row in rows}


def build_resume_index(resume_profile: ResumeProfile, fragments: list[ResumeFragment]) -> ResumeIndex:
    fragment_lookup = {fragment.id: fragment for fragment in fragments}
    fragment_tokens = {fragment.id: set(tokenize(fragment.text)) for fragment in fragments}
    term_locations: dict[str, set[str]] = defaultdict(set)
    skill_terms: set[str] = set()
    skill_section_ids = {fragment.id for fragment in fragments if fragment.section_name == "skills"}
    experience_fragment_ids = {fragment.id for fragment in fragments if fragment.section_name == "experience"}
    project_fragment_ids = {fragment.id for fragment in fragments if fragment.section_name == "projects"}
    education_fragment_ids = {fragment.id for fragment in fragments if fragment.section_name == "education"}
    certification_fragment_ids = {fragment.id for fragment in fragments if fragment.section_name == "certifications"}

    for skill in resume_profile.skills:
        canonical = canonicalize_term(skill.name)
        if not canonical:
            continue
        skill_terms.add(canonical)
        target_ids = skill.evidence_fragment_ids or list(skill_section_ids)
        for fragment_id in target_ids:
            term_locations[canonical].add(fragment_id)
    for experience in resume_profile.experience:
        terms = normalize_terms(experience.technologies + tokenize(" ".join(experience.bullets + [experience.title])))
        for term in terms:
            for fragment_id in experience.evidence_fragment_ids:
                term_locations[term].add(fragment_id)
    for project in resume_profile.projects:
        terms = normalize_terms(project.technologies + tokenize(" ".join(project.bullets + [project.name])))
        for term in terms:
            for fragment_id in project.evidence_fragment_ids:
                term_locations[term].add(fragment_id)
    for fragment in fragments:
        for token in normalize_terms(tokenize(fragment.text)):
            term_locations[token].add(fragment.id)

    return ResumeIndex(
        fragment_lookup=fragment_lookup,
        fragment_tokens=fragment_tokens,
        term_locations=term_locations,
        skill_terms=skill_terms,
        skill_section_ids=skill_section_ids,
        experience_fragment_ids=experience_fragment_ids,
        project_fragment_ids=project_fragment_ids,
        education_fragment_ids=education_fragment_ids,
        certification_fragment_ids=certification_fragment_ids,
    )


def bucket_for_requirement(requirement: RequirementItem) -> str:
    if requirement.category == "required_skill":
        return "required_skills"
    if requirement.category == "preferred_skill":
        return "preferred_skills"
    if requirement.category in {"education", "certification"}:
        return "education"
    if requirement.category == "keyword":
        return "keyword_alignment"
    if requirement.category == "responsibility":
        text = requirement.text.lower()
        return "project_impact" if any(term in text for term in IMPACT_TERMS) else "experience_alignment"
    return "experience_alignment"


def aggregate_signal_scores(
    requirement: RequirementItem,
    bucket: str,
    exact_matches: list[str],
    exact_fragment_ids: set[str],
    lexical_scores: dict[str, float],
    fts_scores: dict[str, float],
    semantic_scores: dict[str, float],
    index: ResumeIndex,
) -> tuple[float, list[str], list[str], str | None]:
    ordered_candidates = sorted(
        index.fragment_lookup,
        key=lambda fragment_id: (
            fragment_id in exact_fragment_ids,
            lexical_scores.get(fragment_id, 0.0),
            fts_scores.get(fragment_id, 0.0),
            semantic_scores.get(fragment_id, 0.0),
        ),
        reverse=True,
    )
    evidence_ids = [
        fragment_id
        for fragment_id in ordered_candidates
        if _is_candidate_relevant(fragment_id, exact_fragment_ids, lexical_scores, semantic_scores)
    ][:3]

    best_lexical = max(lexical_scores.values(), default=0.0)
    best_semantic = max(semantic_scores.values(), default=0.0)
    best_fts = max(fts_scores.values(), default=0.0)
    semantic_component = max((best_semantic - 0.55) / 0.35, 0.0)
    fts_component = min(best_fts / 2.0, 1.0) if best_fts else 0.0
    density_bonus = min(max(len(evidence_ids) - 1, 0) * 0.05, 0.1)

    if requirement.category in {"required_skill", "preferred_skill"}:
        exact_component = 0.55 if exact_matches else 0.0
        if exact_matches and any(fragment_id in index.skill_section_ids for fragment_id in exact_fragment_ids):
            exact_component += 0.1
        if exact_matches and any(
            fragment_id in index.experience_fragment_ids or fragment_id in index.project_fragment_ids
            for fragment_id in exact_fragment_ids
        ):
            exact_component += 0.1
        lexical_component = best_lexical * 0.15
        semantic_component = min(semantic_component * 0.15, 0.15)
    else:
        exact_component = 0.25 if exact_matches else 0.0
        lexical_component = best_lexical * 0.35
        semantic_component = min(semantic_component * 0.25, 0.25)

    score = min(exact_component + lexical_component + (fts_component * 0.15) + semantic_component + density_bonus, 1.0)
    caveat = None
    if score > 0.0 and not exact_matches and best_semantic >= 0.68:
        score = min(score, 0.7)
        caveat = "This is an approximate semantic match rather than an explicit term match."
    if bucket == "keyword_alignment" and not evidence_ids:
        score = best_lexical * 0.4
    matched_terms = exact_matches or _matched_terms_from_candidates(requirement, evidence_ids, index)
    return round(score, 4), evidence_ids, matched_terms, caveat


def build_explanation(
    requirement: RequirementItem,
    strength: str,
    score: float,
    evidence_ids: list[str],
    fragments: dict[str, ResumeFragment],
    caveat: str | None,
    matched_terms: list[str],
) -> str:
    if not evidence_ids:
        return f"No direct resume evidence was found for '{requirement.text}', so it contributes little or nothing to the score."
    section_names = sorted({fragments[fragment_id].section_name for fragment_id in evidence_ids if fragment_id in fragments})
    lead = requirement.text if len(requirement.text) < 80 else requirement.text[:77] + "..."
    explanation = (
        f"{lead} is a {strength.replace('_', ' ')} based on evidence from the "
        f"{', '.join(section_names)} section(s)."
    )
    if matched_terms:
        explanation += f" Matched terms: {', '.join(matched_terms[:4])}."
    if score < 0.5:
        explanation += " The support is limited or indirect."
    if caveat:
        explanation += f" {caveat}"
    return explanation


def strength_from_score(score: float) -> str:
    if score >= 0.75:
        return "strong_match"
    if score >= 0.5:
        return "moderate_match"
    if score >= 0.25:
        return "weak_match"
    return "missing"


def _matched_terms_from_candidates(
    requirement: RequirementItem,
    evidence_ids: list[str],
    index: ResumeIndex,
) -> list[str]:
    requirement_terms = set(normalize_terms(requirement.normalized_terms or tokenize(requirement.text)))
    matched: set[str] = set()
    for fragment_id in evidence_ids:
        matched |= requirement_terms & index.fragment_tokens.get(fragment_id, set())
    return sorted(matched)


def _is_candidate_relevant(
    fragment_id: str,
    exact_fragment_ids: set[str],
    lexical_scores: dict[str, float],
    semantic_scores: dict[str, float],
) -> bool:
    return (
        fragment_id in exact_fragment_ids
        or lexical_scores.get(fragment_id, 0.0) >= 0.2
        or semantic_scores.get(fragment_id, 0.0) >= 0.68
    )

