"""initial schema

Revision ID: 20260316_0001
Revises:
Create Date: 2026-03-16 10:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260316_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "resume_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=16), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "job_postings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "resume_fragments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("resume_document_id", sa.String(length=36), nullable=False),
        sa.Column("section_name", sa.String(length=64), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("block_index", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resume_document_id"], ["resume_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "parsed_resumes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("resume_document_id", sa.String(length=36), nullable=False),
        sa.Column("structured_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resume_document_id"], ["resume_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_document_id"),
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("resume_document_id", sa.String(length=36), nullable=False),
        sa.Column("job_posting_id", sa.String(length=36), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("subscores_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_document_id"], ["resume_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "requirement_matches",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("requirement_id", sa.String(length=64), nullable=False),
        sa.Column("requirement_text", sa.Text(), nullable=False),
        sa.Column("bucket", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("importance", sa.String(length=32), nullable=False),
        sa.Column("match_strength", sa.String(length=32), nullable=False),
        sa.Column("score_contribution", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("matched_terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_fragment_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "suggestions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("suggestion_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("grounded", sa.Boolean(), nullable=False),
        sa.Column("supporting_fragment_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_resume_documents_created_at", "resume_documents", ["created_at"])
    op.create_index("ix_job_postings_created_at", "job_postings", ["created_at"])
    op.create_index("ix_analyses_created_at", "analyses", ["created_at"])
    op.create_index("ix_analyses_resume_document_id", "analyses", ["resume_document_id"])
    op.create_index("ix_analyses_job_posting_id", "analyses", ["job_posting_id"])
    op.create_index("ix_resume_fragments_resume_document_id", "resume_fragments", ["resume_document_id"])
    op.create_index("ix_resume_fragments_section_name", "resume_fragments", ["section_name"])
    op.create_index("ix_requirement_matches_analysis_id", "requirement_matches", ["analysis_id"])
    op.create_index("ix_requirement_matches_match_strength", "requirement_matches", ["match_strength"])
    op.create_index("ix_suggestions_analysis_id", "suggestions", ["analysis_id"])
    op.create_index("ix_suggestions_suggestion_type", "suggestions", ["suggestion_type"])

    op.execute(
        "CREATE INDEX ix_resume_fragments_search ON resume_fragments "
        "USING gin (to_tsvector('english', text))"
    )
    op.execute(
        "CREATE INDEX ix_resume_fragments_embedding ON resume_fragments "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_resume_fragments_embedding")
    op.execute("DROP INDEX IF EXISTS ix_resume_fragments_search")
    op.drop_index("ix_suggestions_suggestion_type", table_name="suggestions")
    op.drop_index("ix_suggestions_analysis_id", table_name="suggestions")
    op.drop_index("ix_requirement_matches_match_strength", table_name="requirement_matches")
    op.drop_index("ix_requirement_matches_analysis_id", table_name="requirement_matches")
    op.drop_index("ix_resume_fragments_section_name", table_name="resume_fragments")
    op.drop_index("ix_resume_fragments_resume_document_id", table_name="resume_fragments")
    op.drop_index("ix_analyses_job_posting_id", table_name="analyses")
    op.drop_index("ix_analyses_resume_document_id", table_name="analyses")
    op.drop_index("ix_analyses_created_at", table_name="analyses")
    op.drop_index("ix_job_postings_created_at", table_name="job_postings")
    op.drop_index("ix_resume_documents_created_at", table_name="resume_documents")

    op.drop_table("suggestions")
    op.drop_table("requirement_matches")
    op.drop_table("analyses")
    op.drop_table("parsed_resumes")
    op.drop_table("resume_fragments")
    op.drop_table("job_postings")
    op.drop_table("resume_documents")

