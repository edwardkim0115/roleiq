from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.analysis import Analysis, RequirementMatch, Suggestion
from app.models.job import JobPosting
from app.models.resume import ParsedResume, ResumeDocument, ResumeFragment
from app.schemas.analysis import DocumentPreview
from app.schemas.domain import JobProfile, ResumeProfile
from app.services.document_ingestion import DocumentExtractor
from app.services.embeddings import EmbeddingService
from app.services.job_parser import JobParser
from app.services.matching import MatchEngine
from app.services.openai_client import OpenAIService
from app.services.resume_parser import ResumeParser
from app.services.scoring import score_evaluations
from app.services.suggestions import SuggestionEngine


@dataclass
class ParsedAnalysisArtifacts:
    resume_document: ResumeDocument
    parsed_resume: ResumeProfile
    job_posting: JobPosting
    job_profile: JobProfile
    fragments: list[ResumeFragment]
    analysis: Analysis


class AnalysisPipeline:
    def __init__(self, session: Session, extractor: DocumentExtractor) -> None:
        self.session = session
        self.extractor = extractor
        self.openai_service = OpenAIService()
        self.resume_parser = ResumeParser(self.openai_service)
        self.job_parser = JobParser(self.openai_service)
        self.embedding_service = EmbeddingService(self.openai_service)
        self.match_engine = MatchEngine(session)
        self.suggestion_engine = SuggestionEngine(self.openai_service)

    def preview_resume(self, filename: str, payload: bytes) -> DocumentPreview:
        extracted = self.extractor.extract(filename, payload)
        parsed_resume = self.resume_parser.parse(extracted.fragments)
        return DocumentPreview(
            filename=extracted.filename,
            file_type=extracted.file_type,
            raw_text=extracted.raw_text,
            fragments=parsed_resume.text_fragments,
        )

    def preview_job(self, job_text: str) -> JobProfile:
        return self.job_parser.parse(job_text)

    def run(
        self,
        filename: str,
        payload: bytes,
        job_text: str,
        job_label: str | None = None,
    ) -> ParsedAnalysisArtifacts:
        extracted = self.extractor.extract(filename, payload)
        parsed_resume = self.resume_parser.parse(extracted.fragments)
        job_profile = self.job_parser.parse(job_text)
        if job_label:
            job_profile = job_profile.model_copy(update={"title": job_label})

        resume_document = ResumeDocument(
            filename=extracted.filename,
            file_type=extracted.file_type,
            raw_text=extracted.raw_text,
        )
        self.session.add(resume_document)
        self.session.flush()

        fragment_models = [
            ResumeFragment(
                id=fragment.id,
                resume_document_id=resume_document.id,
                section_name=fragment.section_name,
                order_index=fragment.order_index,
                text=fragment.text,
                page_number=fragment.page_number,
                block_index=fragment.block_index,
                metadata_json={
                    "source_type": fragment.source_type,
                    "char_start": fragment.char_start,
                    "char_end": fragment.char_end,
                },
            )
            for fragment in parsed_resume.text_fragments
        ]
        self.session.add_all(fragment_models)

        self.session.add(
            ParsedResume(
                resume_document_id=resume_document.id,
                structured_json=parsed_resume.model_dump(mode="json"),
            )
        )

        job_posting = JobPosting(
            title=job_profile.title,
            company=job_profile.company,
            raw_text=job_text,
            structured_json=job_profile.model_dump(mode="json"),
        )
        self.session.add(job_posting)
        self.session.flush()

        self.embedding_service.embed_resume_fragments(self.session, fragment_models)
        requirement_embeddings = self.embedding_service.embed_requirement_texts(
            [requirement.text for requirement in job_profile.raw_requirement_items]
        )

        evaluations = self.match_engine.evaluate(
            resume_profile=parsed_resume,
            job_profile=job_profile,
            fragments=fragment_models,
            requirement_embeddings=requirement_embeddings,
        )
        overall_score, buckets, summary = score_evaluations(evaluations)

        fragment_lookup = {fragment.id: fragment.text for fragment in fragment_models}
        tailored_summary, suggestion_drafts = self.suggestion_engine.generate(
            evaluations=evaluations,
            fragment_lookup=fragment_lookup,
            summary=summary,
        )
        if tailored_summary:
            summary["tailored_summary"] = tailored_summary

        analysis = Analysis(
            resume_document_id=resume_document.id,
            job_posting_id=job_posting.id,
            overall_score=overall_score,
            subscores_json={"buckets": [bucket.model_dump(mode="json") for bucket in buckets]},
            summary_json=summary,
        )
        self.session.add(analysis)
        self.session.flush()

        for evaluation in evaluations:
            self.session.add(
                RequirementMatch(
                    analysis_id=analysis.id,
                    requirement_id=evaluation.requirement.id,
                    requirement_text=evaluation.requirement.text,
                    bucket=evaluation.bucket,
                    category=evaluation.requirement.category,
                    importance=evaluation.requirement.importance,
                    match_strength=evaluation.match_strength,
                    score_contribution=evaluation.score_contribution,
                    confidence_score=evaluation.confidence_score,
                    explanation=evaluation.explanation,
                    matched_terms=evaluation.matched_terms,
                    missing_terms=evaluation.missing_terms,
                    evidence_fragment_ids=evaluation.evidence_fragment_ids,
                )
            )

        for draft in suggestion_drafts:
            self.session.add(
                Suggestion(
                    analysis_id=analysis.id,
                    suggestion_type=draft.suggestion_type,
                    title=draft.title,
                    body=draft.body,
                    grounded=draft.grounded,
                    supporting_fragment_ids=draft.supporting_fragment_ids,
                )
            )

        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return ParsedAnalysisArtifacts(
            resume_document=resume_document,
            parsed_resume=parsed_resume,
            job_posting=job_posting,
            job_profile=job_profile,
            fragments=fragment_models,
            analysis=analysis,
        )
