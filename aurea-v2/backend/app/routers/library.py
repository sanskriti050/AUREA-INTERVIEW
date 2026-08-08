from fastapi import APIRouter, HTTPException
from app.services.answer_library import get_topics, get_questions, get_question

router = APIRouter(prefix="/library", tags=["Answer Library"])


@router.get("/topics")
def topics():
    return {"topics": get_topics()}


@router.get("/questions/{topic}/{difficulty}")
def questions(topic: str, difficulty: str):
    qs = get_questions(topic, difficulty)
    if not qs:
        raise HTTPException(status_code=404, detail="No library entries for this combination.")
    return {"questions": qs, "total": len(qs)}


@router.get("/question/{topic}/{difficulty}/{qid}")
def question(topic: str, difficulty: str, qid: str):
    q = get_question(topic, difficulty, qid)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    return q
