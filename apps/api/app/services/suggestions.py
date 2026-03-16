from __future__ import annotations

from dataclasses import dataclass

from app.services.matching import RequirementEvaluation
from app.services.openai_client import OpenAIService
from app.utils.text import clean_text


@dataclass
class SuggestionDraft:
    suggestion_type: str
    title: str
    body: str
    grounded: bool
    supporting_fragment_ids: list[str]


class SuggestionEngine:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai_service = openai_service or OpenAIService()

    def generate(
        self,
        evaluations: list[RequirementEvaluation],
        fragment_lookup: dict[str, str],
        summary: dict,
    ) -> tuple[str | None, list[SuggestionDraft]]:
        drafts = build_deterministic_suggestions(evaluations, fragment_lookup)
        refined_summary = self._generate_summary_with_model(drafts, fragment_lookup, summary)
        return refined_summary, drafts

    def _generate_summary_with_model(
        self,
        drafts: list[SuggestionDraft],
        fragment_lookup: dict[str, str],
        summary: dict,
    ) -> str | None:
        payload = {
            "summary": summary,
            "draft_suggestions": [draft.__dict__ for draft in drafts[:5]],
            "fragments": [{"id": key, "text": value} for key, value in list(fragment_lookup.items())[:12]],
        }
        response = self.openai_service.generate_grounded_suggestions(payload)
        if not response:
            return None
        return response.tailored_summary


def build_deterministic_suggestions(
    evaluations: list[RequirementEvaluation],
    fragment_lookup: dict[str, str],
) -> list[SuggestionDraft]:
    drafts: list[SuggestionDraft] = []
    seen_titles: set[str] = set()

    for evaluation in evaluations:
        terms = evaluation.requirement.normalized_terms or [evaluation.requirement.text]
        focus_label = terms[0] if terms else evaluation.requirement.text
        if evaluation.match_strength in {"moderate_match", "weak_match"} and evaluation.evidence_fragment_ids:
            evidence_text = fragment_lookup.get(evaluation.evidence_fragment_ids[0], "")
            title = f"Make {focus_label} more explicit"
            body = (
                f"The resume has some support for {focus_label}, but the evidence is indirect. "
                f"Consider tightening the wording around this requirement in the supporting bullet if it is accurate. "
                f"Current evidence: {truncate_text(evidence_text)}"
            )
            _append_unique(
                drafts,
                seen_titles,
                SuggestionDraft(
                    suggestion_type="phrasing",
                    title=title,
                    body=body,
                    grounded=True,
                    supporting_fragment_ids=evaluation.evidence_fragment_ids,
                ),
            )
        if evaluation.requirement.category in {"required_skill", "preferred_skill"} and evaluation.evidence_fragment_ids:
            title = f"Surface {focus_label} higher in the resume"
            body = (
                f"{focus_label} is supported in the resume, but making it more visible near the skills inventory or top-most relevant bullets "
                f"could help this job match read more clearly."
            )
            _append_unique(
                drafts,
                seen_titles,
                SuggestionDraft(
                    suggestion_type="emphasis",
                    title=title,
                    body=body,
                    grounded=True,
                    supporting_fragment_ids=evaluation.evidence_fragment_ids,
                ),
            )
        if evaluation.match_strength == "missing":
            title = f"Treat {focus_label} as a real gap"
            body = (
                f"The job posting explicitly asks for {focus_label}, and the resume does not currently show direct evidence for it. "
                f"Do not add it unless you have real experience or coursework to support it."
            )
            _append_unique(
                drafts,
                seen_titles,
                SuggestionDraft(
                    suggestion_type="gap",
                    title=title,
                    body=body,
                    grounded=False,
                    supporting_fragment_ids=[],
                ),
            )

    return drafts[:8]


def truncate_text(value: str, limit: int = 180) -> str:
    collapsed = clean_text(value)
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


def _append_unique(
    drafts: list[SuggestionDraft],
    seen_titles: set[str],
    draft: SuggestionDraft,
) -> None:
    if draft.title in seen_titles:
        return
    seen_titles.add(draft.title)
    drafts.append(draft)

