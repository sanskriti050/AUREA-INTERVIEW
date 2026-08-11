"""Persistent resume embeddings.

PostgreSQL uses pgvector's native VECTOR type. SQLite stores the same value as
JSON so local development and tests continue to work without Docker/Postgres.
"""
from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
from app.core.database import Base


class EmbeddingVector(TypeDecorator):
    """Use VECTOR in PostgreSQL when pgvector is installed, JSON elsewhere."""
    impl = JSON
    cache_ok = True

    def __init__(self, dimensions: int = 1536, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector
            except ImportError as exc:
                raise RuntimeError("PostgreSQL vector support requires the 'pgvector' package.") from exc
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON())


class ResumeEmbedding(Base):
    __tablename__ = "resume_embeddings"

    id = Column(String, primary_key=True)
    resume_id = Column(String, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    embedding = Column(EmbeddingVector(1536), nullable=False)
    model = Column(String(120), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
