from __future__ import annotations

from collections import defaultdict

from app.schemas.analysis import SubscoreBucket
from app.services.matching import BUCKET_SPECS, RequirementEvaluation


def score_evaluations(evaluations: list[RequirementEvaluation]) -> tuple[float, list[SubscoreBucket], dict]:
    grouped: dict[str, list[RequirementEvaluation]] = defaultdict(list)
    for evaluation in evaluations:
        grouped[evaluation.bucket].append(evaluation)

    buckets: list[SubscoreBucket] = []
    earned_total = 0.0
    possible_total = 0.0

    for key, spec in BUCKET_SPECS.items():
        bucket_evaluations = grouped.get(key, [])
        if not bucket_evaluations:
            buckets.append(
                SubscoreBucket(
                    key=key,
                    label=spec["label"],
                    weight=spec["weight"],
                    earned_points=0.0,
                    possible_points=0.0,
                    normalized_score=None,
                    applicable=False,
                    matched_requirements=0,
                    total_requirements=0,
                )
            )
            continue

        max_per_requirement = spec["weight"] / len(bucket_evaluations)
        earned_points = 0.0
        for evaluation in bucket_evaluations:
            evaluation.score_contribution = round(max_per_requirement * evaluation.confidence_score, 2)
            earned_points += evaluation.score_contribution
        earned_total += earned_points
        possible_total += spec["weight"]
        buckets.append(
            SubscoreBucket(
                key=key,
                label=spec["label"],
                weight=spec["weight"],
                earned_points=round(earned_points, 2),
                possible_points=float(spec["weight"]),
                normalized_score=round((earned_points / spec["weight"]) * 100, 1),
                applicable=True,
                matched_requirements=sum(
                    1 for evaluation in bucket_evaluations if evaluation.match_strength != "missing"
                ),
                total_requirements=len(bucket_evaluations),
            )
        )

    overall_score = round((earned_total / possible_total) * 100, 1) if possible_total else 0.0
    summary = build_summary(evaluations)
    return overall_score, buckets, summary


def build_summary(evaluations: list[RequirementEvaluation]) -> dict:
    ranked_strengths = sorted(
        [item for item in evaluations if item.match_strength != "missing"],
        key=lambda item: (item.score_contribution, item.confidence_score),
        reverse=True,
    )
    ranked_gaps = sorted(
        [item for item in evaluations if item.match_strength in {"missing", "weak_match"}],
        key=lambda item: (item.match_strength != "missing", item.confidence_score),
    )

    top_strengths = [item.requirement.text for item in ranked_strengths[:3]]
    top_gaps = [item.requirement.text for item in ranked_gaps[:3]]
    notes = []
    if any(item.match_strength == "missing" and item.requirement.importance == "required" for item in evaluations):
        notes.append("Missing required items are reducing the score more than preferred gaps.")
    if any(item.match_strength == "moderate_match" and not item.matched_terms for item in evaluations):
        notes.append("Some matches are approximate and based on semantic evidence rather than exact wording.")
    return {
        "top_strengths": top_strengths,
        "top_gaps": top_gaps,
        "notes": notes,
    }

