from __future__ import annotations

import json
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.schemas.domain import JobProfile, ResumeProfile, TextFragment
from app.schemas.llm import GroundedSuggestionPayload

settings = get_settings()

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class OpenAIService:
    def __init__(self) -> None:
        self._client = (
            OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)
            if settings.openai_api_key
            else None
        )

    @property
    def enabled(self) -> bool:
        return self._client is not None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _parse_schema(self, schema: type[SchemaT], system_prompt: str, payload: dict) -> SchemaT:
        if not self._client:
            raise RuntimeError("OpenAI API key is not configured")
        response = self._client.responses.parse(
            model=settings.openai_parser_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=True)},
            ],
            text_format=schema,
        )
        if response.output_parsed is None:
            raise ValueError("Structured parsing returned no parsed output")
        return response.output_parsed

    def parse_resume(self, fragments: list[TextFragment], raw_sections: list[dict]) -> ResumeProfile | None:
        if not self.enabled:
            return None
        payload = {
            "instructions": "Use only the provided fragment ids as evidence references.",
            "fragments": [fragment.model_dump() for fragment in fragments],
            "raw_sections": raw_sections,
        }
        system_prompt = (
            "Extract a structured resume profile. "
            "Do not invent facts. Only use evidence_fragment_ids that exist in the provided fragments. "
            "If a field is missing, return null or an empty list."
        )
        return self._parse_schema(ResumeProfile, system_prompt, payload)

    def parse_job(self, job_text: str) -> JobProfile | None:
        if not self.enabled:
            return None
        payload = {"job_text": job_text}
        system_prompt = (
            "Extract a structured job profile from the job posting. "
            "Break the posting into explicit requirement items. "
            "Use category values exactly as defined by the schema and avoid duplicate requirements."
        )
        return self._parse_schema(JobProfile, system_prompt, payload)

    def embed_texts(self, texts: list[str]) -> list[list[float]] | None:
        if not self.enabled or not texts:
            return None
        response = self._client.embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [list(item.embedding) for item in response.data]

    def generate_grounded_suggestions(self, payload: dict) -> GroundedSuggestionPayload | None:
        if not self.enabled:
            return None
        system_prompt = (
            "Generate grounded resume-improvement suggestions for a single job application. "
            "Do not invent experience, tools, or achievements. "
            "If there is no supporting evidence, mark the suggestion as ungrounded and say the gap is real."
        )
        return self._parse_schema(GroundedSuggestionPayload, system_prompt, payload)

