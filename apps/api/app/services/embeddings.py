from __future__ import annotations

from math import sqrt

from sqlalchemy.orm import Session

from app.models.resume import ResumeFragment
from app.services.openai_client import OpenAIService


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(a * a for a in left))
    right_norm = sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


class EmbeddingService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai_service = openai_service or OpenAIService()

    def embed_resume_fragments(self, session: Session, fragments: list[ResumeFragment]) -> None:
        if not fragments:
            return
        texts = [fragment.text for fragment in fragments]
        embeddings = self.openai_service.embed_texts(texts)
        if not embeddings:
            return
        for fragment, embedding in zip(fragments, embeddings, strict=False):
            fragment.embedding = embedding
            session.add(fragment)

    def embed_requirement_texts(self, requirements: list[str]) -> dict[str, list[float]]:
        embeddings = self.openai_service.embed_texts(requirements)
        if not embeddings:
            return {}
        return {text: embedding for text, embedding in zip(requirements, embeddings, strict=False)}

