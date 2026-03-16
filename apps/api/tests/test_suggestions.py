from __future__ import annotations

from app.services.suggestions import build_deterministic_suggestions
from tests.helpers import sample_evaluations, sample_fragment_lookup


def test_grounded_suggestions_only_reference_existing_fragments():
    evaluations = sample_evaluations()
    fragment_lookup = sample_fragment_lookup()

    suggestions = build_deterministic_suggestions(evaluations, fragment_lookup)
    valid_ids = set(fragment_lookup)

    assert suggestions
    for suggestion in suggestions:
        assert set(suggestion.supporting_fragment_ids).issubset(valid_ids)
        if suggestion.grounded:
            assert suggestion.supporting_fragment_ids
        else:
            assert not suggestion.supporting_fragment_ids
            assert "does not currently show direct evidence" in suggestion.body
