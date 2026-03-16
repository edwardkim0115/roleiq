from __future__ import annotations

from app.schemas.domain import RequirementItem
from app.services.matching import RequirementEvaluation
from app.services.scoring import score_evaluations


def test_scoring_respects_bucket_weights():
    evaluations = [
        RequirementEvaluation(
            requirement=RequirementItem(
                id="1",
                text="Python",
                category="required_skill",
                importance="required",
                normalized_terms=["python"],
            ),
            bucket="required_skills",
            confidence_score=1.0,
            match_strength="strong_match",
            explanation="matched",
        ),
        RequirementEvaluation(
            requirement=RequirementItem(
                id="2",
                text="Kubernetes",
                category="preferred_skill",
                importance="preferred",
                normalized_terms=["kubernetes"],
            ),
            bucket="preferred_skills",
            confidence_score=0.0,
            match_strength="missing",
            explanation="missing",
        ),
    ]

    overall, buckets, summary = score_evaluations(evaluations)
    bucket_map = {bucket.key: bucket for bucket in buckets}

    assert overall == 66.7
    assert bucket_map["required_skills"].earned_points == 30.0
    assert bucket_map["preferred_skills"].earned_points == 0.0
    assert "Python" in summary["top_strengths"]
    assert "Kubernetes" in summary["top_gaps"]

