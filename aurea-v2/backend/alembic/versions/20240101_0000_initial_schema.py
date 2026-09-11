"""Initial schema — all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

This migration is idempotent: if tables already exist (created by SQLAlchemy's
create_all during early development), it skips creation and just stamps the
revision. This lets both fresh installs (PostgreSQL/Docker) and existing SQLite
dev databases use the same migration history.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"
    inspector = inspect(bind)

    # ── pgvector extension (PostgreSQL only) ──────────────────────────────────
    if is_pg:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── Idempotency guard ─────────────────────────────────────────────────────
    # If the users table already exists the schema was created via create_all.
    # Skip DDL — the stamp command already recorded this revision.
    if inspector.has_table("users"):
        return

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("google_id", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)

    # ── resumes ───────────────────────────────────────────────────────────────
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("top_role", sa.String(100), nullable=True),
        sa.Column("role_matches", sa.JSON(), nullable=True),
        sa.Column("tips", sa.JSON(), nullable=True),
        sa.Column("roadmap", sa.JSON(), nullable=True),
        sa.Column("sections", sa.JSON(), nullable=True),
        sa.Column("quantified_bullets", sa.Integer(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column("email_detected", sa.String(), nullable=True),
        sa.Column("github_detected", sa.String(), nullable=True),
        sa.Column("linkedin_detected", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # ── resume_embeddings ─────────────────────────────────────────────────────
    if is_pg:
        # Native VECTOR(1536) column via raw DDL — pgvector type not in SA core
        op.create_table(
            "resume_embeddings",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("resume_id", sa.String(), nullable=False),
            sa.Column("model", sa.String(120), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("resume_id"),
        )
        op.execute("ALTER TABLE resume_embeddings ADD COLUMN embedding vector(1536) NOT NULL")
    else:
        # SQLite: store vector as JSON array
        op.create_table(
            "resume_embeddings",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("resume_id", sa.String(), nullable=False),
            sa.Column("embedding", sa.JSON(), nullable=False),
            sa.Column("model", sa.String(120), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("resume_id"),
        )
    op.create_index("ix_resume_embeddings_resume_id", "resume_embeddings", ["resume_id"], unique=True)

    # ── interview_sessions ────────────────────────────────────────────────────
    session_type_col = sa.String(20)





    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("session_type", session_type_col, nullable=False),
        sa.Column("topic", sa.String(100), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=True),
        sa.Column("answered", sa.Integer(), nullable=True),
        sa.Column("transcript", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── progress_events ───────────────────────────────────────────────────────
    event_type_col = sa.String(30)





    op.create_table(
        "progress_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("event_type", event_type_col, nullable=False),
        sa.Column("topic", sa.String(100), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── quiz_questions ────────────────────────────────────────────────────────
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_index", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quiz_questions_topic", "quiz_questions", ["topic"])
    op.create_index("ix_quiz_questions_difficulty", "quiz_questions", ["difficulty"])


def downgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    op.drop_index("ix_quiz_questions_difficulty", table_name="quiz_questions")
    op.drop_index("ix_quiz_questions_topic", table_name="quiz_questions")
    op.drop_table("quiz_questions")
    op.drop_table("progress_events")
    op.drop_table("interview_sessions")
    op.drop_index("ix_resume_embeddings_resume_id", table_name="resume_embeddings")
    op.drop_table("resume_embeddings")
    op.drop_table("resumes")
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    if is_pg:
        op.execute("DROP TYPE IF EXISTS eventtype")
        op.execute("DROP TYPE IF EXISTS sessiontype")
