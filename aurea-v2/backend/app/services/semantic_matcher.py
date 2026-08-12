"""Embedding-backed semantic resume ↔ job-description matching.

An OpenAI-compatible embeddings API is intentionally configurable so the
application is not coupled to one vendor. The lexical matcher remains a safe
offline fallback for local demos where no embedding key is configured.
"""
from __future__ import annotations

import math
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.resume_embedding import ResumeEmbedding
from app.services.jd_matcher import match_jd


def embeddings_enabled() -> bool:
    return bool(settings.EMBEDDING_API_KEY)


async def create_embedding(text: str) -> list[float] | None:
    """Return a 1536-dimension embedding, or None when semantic search is off."""
    if not embeddings_enabled():
        return None
    base_url = settings.EMBEDDING_BASE_URL.rstrip("/")
    headers = {"Authorization": f"Bearer {settings.EMBEDDING_API_KEY}"}
    payload = {"model": settings.EMBEDDING_MODEL, "input": text[:24000]}
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(f"{base_url}/embeddings", headers=headers, json=payload)
            response.raise_for_status()
        vector = response.json()["data"][0]["embedding"]
        return vector if isinstance(vector, list) and len(vector) == 1536 else None
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        return None


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left)) or 1.0
    norm_right = math.sqrt(sum(b * b for b in right)) or 1.0
    return max(0.0, min(1.0, dot / (norm_left * norm_right)))


async def store_resume_embedding(db: Session, resume_id: str, resume_text: str) -> bool:
    """Upsert a resume vector after upload; no-op when embeddings are not configured."""
    vector = await create_embedding(resume_text)
    if vector is None:
        return False
    record = db.query(ResumeEmbedding).filter(ResumeEmbedding.resume_id == resume_id).first()
    if record is None:
        record = ResumeEmbedding(id=str(uuid4()), resume_id=resume_id, embedding=vector, model=settings.EMBEDDING_MODEL)
        db.add(record)
    else:
        record.embedding = vector
        record.model = settings.EMBEDDING_MODEL
    db.commit()
    return True


async def semantic_match_jd(db: Session, resume_id: str, resume_text: str, jd_text: str) -> dict:
    """Use vectors when available, preserving explainable keyword evidence."""
    lexical = match_jd(resume_text, jd_text)
    stored = db.query(ResumeEmbedding).filter(ResumeEmbedding.resume_id == resume_id).first()
    jd_vector = await create_embedding(jd_text)
    if stored is None or jd_vector is None or not isinstance(stored.embedding, list):
        lexical["match_method"] = "keyword analysis (set EMBEDDING_API_KEY for semantic matching)"
        return lexical

    semantic_score = round(_cosine_similarity(stored.embedding, jd_vector) * 100)
    # Blend semantic fit with lexical ATS evidence: semantic meaning should guide
    # the score, but matched/missing terms remain visible and explainable.
    lexical_score = lexical["match_score"]
    lexical["match_score"] = round(semantic_score * 0.7 + lexical_score * 0.3)
    lexical["semantic_score"] = semantic_score
    lexical["match_method"] = "semantic embeddings + keyword evidence"
    lexical["suggestions"] = [
        f"Semantic fit is {semantic_score}%. Keyword coverage is {lexical_score}%.",
        *lexical["suggestions"],
    ]
    return lexical
