from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.analysis import Analysis, RequirementMatch, Suggestion
from app.models.job import JobPosting
from app.models.resume import ResumeDocument, ResumeFragment
from app.schemas.analysis import (
    AnalysisDetail,
    AnalysisListItem,
    DocumentPreview,
    JobParseRequest,
    RequirementMatchRead,
    ResumeDocumentRead,
    ResumeFragmentRead,
    ScoreRead,
    SuggestionRead,
)
from app.schemas.domain import JobProfile, ResumeProfile
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.document_ingestion import DocumentExtractionError, DocumentExtractor

router = APIRouter(tags=["analyses"])
settings = get_settings()


def get_pipeline(session: Session) -> AnalysisPipeline:
    extractor = DocumentExtractor(max_size_bytes=settings.max_upload_size_bytes)
    return AnalysisPipeline(session=session, extractor=extractor)


@router.post("/resumes/upload", response_model=DocumentPreview)
async def preview_resume_upload(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> DocumentPreview:
    pipeline = get_pipeline(session)
    payload = await file.read()
    try:
        return pipeline.preview_resume(file.filename or "resume.txt", payload)
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/jobs/parse-text", response_model=JobProfile)
def parse_job_text(
    request: JobParseRequest,
    session: Session = Depends(get_db_session),
) -> JobProfile:
    return get_pipeline(session).preview_job(request.job_text)


@router.post("/analyses", response_model=AnalysisDetail, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    job_text: str = Form(...),
    job_label: str | None = Form(default=None),
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> AnalysisDetail:
    pipeline = get_pipeline(session)
    payload = await file.read()
    try:
        artifacts = pipeline.run(file.filename or "resume.txt", payload, job_text, job_label)
    except DocumentExtractionError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety path
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        ) from exc
    return get_analysis(artifacts.analysis.id, session)


@router.get("/analyses", response_model=list[AnalysisListItem])
def list_analyses(
    q: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[AnalysisListItem]:
    statement = (
        select(Analysis)
        .join(Analysis.job_posting)
        .join(Analysis.resume_document)
        .options(selectinload(Analysis.job_posting), selectinload(Analysis.resume_document))
        .order_by(Analysis.created_at.desc())
    )
    if q:
        like = f"%{q}%"
        statement = statement.where(
            or_(
                JobPosting.title.ilike(like),
                JobPosting.company.ilike(like),
                ResumeDocument.filename.ilike(like),
            )
        )
    analyses = session.execute(statement).scalars().all()
    return [
        AnalysisListItem(
            id=analysis.id,
            title=analysis.job_posting.title or "Untitled job",
            company=analysis.job_posting.company,
            filename=analysis.resume_document.filename,
            overall_score=analysis.overall_score,
            created_at=analysis.created_at,
            top_strengths=analysis.summary_json.get("top_strengths", []),
            top_gaps=analysis.summary_json.get("top_gaps", []),
        )
        for analysis in analyses
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> AnalysisDetail:
    analysis = _load_analysis(session, analysis_id)
    return _serialize_analysis(analysis)


@router.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> Response:
    analysis = _load_analysis(session, analysis_id)
    resume_document_id = analysis.resume_document_id
    job_posting_id = analysis.job_posting_id
    session.delete(analysis)
    session.flush()

    remaining_resume_uses = session.scalar(
        select(func.count()).select_from(Analysis).where(Analysis.resume_document_id == resume_document_id)
    )
    if not remaining_resume_uses:
        resume_document = session.get(ResumeDocument, resume_document_id)
        if resume_document:
            session.delete(resume_document)

    remaining_job_uses = session.scalar(
        select(func.count()).select_from(Analysis).where(Analysis.job_posting_id == job_posting_id)
    )
    if not remaining_job_uses:
        job_posting = session.get(JobPosting, job_posting_id)
        if job_posting:
            session.delete(job_posting)

    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/analyses/{analysis_id}/parsed-resume", response_model=ResumeProfile)
def get_parsed_resume(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> ResumeProfile:
    analysis = _load_analysis(session, analysis_id)
    if not analysis.resume_document.parsed_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parsed resume not found")
    return ResumeProfile.model_validate(analysis.resume_document.parsed_resume.structured_json)


@router.get("/analyses/{analysis_id}/parsed-job", response_model=JobProfile)
def get_parsed_job(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> JobProfile:
    analysis = _load_analysis(session, analysis_id)
    return JobProfile.model_validate(analysis.job_posting.structured_json)


@router.get("/analyses/{analysis_id}/score", response_model=ScoreRead)
def get_analysis_score(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> ScoreRead:
    analysis = _load_analysis(session, analysis_id)
    return ScoreRead(
        analysis_id=analysis.id,
        overall_score=analysis.overall_score,
        subscores=_deserialize_subscores(analysis.subscores_json),
        summary=analysis.summary_json,
    )


@router.get("/analyses/{analysis_id}/requirements", response_model=list[RequirementMatchRead])
def get_analysis_requirements(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> list[RequirementMatchRead]:
    analysis = _load_analysis(session, analysis_id)
    return [_serialize_requirement(match) for match in analysis.requirement_matches]


@router.get("/analyses/{analysis_id}/suggestions", response_model=list[SuggestionRead])
def get_analysis_suggestions(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> list[SuggestionRead]:
    analysis = _load_analysis(session, analysis_id)
    return [_serialize_suggestion(item) for item in analysis.suggestions]


@router.get("/analyses/{analysis_id}/evidence", response_model=list[ResumeFragmentRead])
def get_analysis_evidence(
    analysis_id: str,
    session: Session = Depends(get_db_session),
) -> list[ResumeFragmentRead]:
    analysis = _load_analysis(session, analysis_id)
    return [_serialize_fragment(fragment) for fragment in analysis.resume_document.fragments]


def _load_analysis(session: Session, analysis_id: str) -> Analysis:
    statement = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(
            selectinload(Analysis.resume_document).selectinload(ResumeDocument.fragments),
            selectinload(Analysis.resume_document).selectinload(ResumeDocument.parsed_resume),
            selectinload(Analysis.job_posting),
            selectinload(Analysis.requirement_matches),
            selectinload(Analysis.suggestions),
        )
    )
    analysis = session.execute(statement).scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


def _serialize_analysis(analysis: Analysis) -> AnalysisDetail:
    parsed_resume_row = analysis.resume_document.parsed_resume
    if not parsed_resume_row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Parsed resume missing")
    return AnalysisDetail(
        id=analysis.id,
        overall_score=analysis.overall_score,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        resume_document=ResumeDocumentRead(
            id=analysis.resume_document.id,
            filename=analysis.resume_document.filename,
            file_type=analysis.resume_document.file_type,
            raw_text=analysis.resume_document.raw_text,
            created_at=analysis.resume_document.created_at,
        ),
        fragments=[_serialize_fragment(fragment) for fragment in analysis.resume_document.fragments],
        parsed_resume=ResumeProfile.model_validate(parsed_resume_row.structured_json),
        job_posting=JobProfile.model_validate(analysis.job_posting.structured_json),
        subscores=_deserialize_subscores(analysis.subscores_json),
        summary=analysis.summary_json,
        requirements=[_serialize_requirement(match) for match in analysis.requirement_matches],
        suggestions=[_serialize_suggestion(item) for item in analysis.suggestions],
    )


def _serialize_fragment(fragment: ResumeFragment) -> ResumeFragmentRead:
    return ResumeFragmentRead(
        id=fragment.id,
        section_name=fragment.section_name,
        order_index=fragment.order_index,
        text=fragment.text,
        page_number=fragment.page_number,
        block_index=fragment.block_index,
        metadata=fragment.metadata_json,
        created_at=fragment.created_at,
    )


def _serialize_requirement(match: RequirementMatch) -> RequirementMatchRead:
    return RequirementMatchRead(
        id=match.id,
        requirement_id=match.requirement_id,
        requirement_text=match.requirement_text,
        bucket=match.bucket,
        category=match.category,
        importance=match.importance,
        match_strength=match.match_strength,
        score_contribution=match.score_contribution,
        confidence_score=match.confidence_score,
        explanation=match.explanation,
        matched_terms=match.matched_terms,
        missing_terms=match.missing_terms,
        evidence_fragment_ids=match.evidence_fragment_ids,
    )


def _serialize_suggestion(item: Suggestion) -> SuggestionRead:
    return SuggestionRead(
        id=item.id,
        suggestion_type=item.suggestion_type,
        title=item.title,
        body=item.body,
        grounded=item.grounded,
        supporting_fragment_ids=item.supporting_fragment_ids,
        created_at=item.created_at,
    )


def _deserialize_subscores(payload: dict) -> list:
    return [bucket for bucket in payload.get("buckets", [])]
