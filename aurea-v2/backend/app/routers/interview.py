from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession
from app.schemas.interview import (
    TheoryQuestionRequest, EvaluateAnswerRequest, EvaluateAnswerResponse,
    AIFeedbackRequest, SessionCreateRequest, SessionResponse
    , SessionCompleteRequest
)
import json

from app.services.interview_engine import question_set, evaluate_theory, ROLES, THEORY_TOPICS, DIFFICULTIES
from app.services.ai_service import stream_ai_feedback
from app.models.progress import ProgressEvent, EventType

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.get("/roles")
def get_roles():
    return {"roles": ROLES}


@router.get("/topics")
def get_topics():
    return {"topics": THEORY_TOPICS}


@router.get("/difficulties")
def get_difficulties():
    return {"difficulties": DIFFICULTIES}


@router.post("/questions")
def get_questions(payload: TheoryQuestionRequest):
    if payload.topic not in THEORY_TOPICS:
        raise HTTPException(status_code=400, detail=f"Invalid topic.")
    if payload.difficulty not in DIFFICULTIES:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty.")
    if payload.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role.")
    questions = question_set(payload.role, payload.topic, payload.difficulty, payload.skills)
    count = getattr(payload, "count", 10)
    questions = questions[:count]
    return {"questions": questions}


@router.post("/evaluate", response_model=EvaluateAnswerResponse)
def evaluate(payload: EvaluateAnswerRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = evaluate_theory(payload.answer, payload.topic, payload.difficulty, payload.question)
    db.add(ProgressEvent(user_id=current_user.id, event_type=EventType.theory_evaluated,
                         topic=payload.topic, difficulty=payload.difficulty, score=result["score"],
                         payload={"question": payload.question[:500]}))
    db.commit()
    return EvaluateAnswerResponse(**result)


@router.post("/ai-feedback/stream")
async def ai_feedback_stream(
    payload: AIFeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream AI feedback using Server-Sent Events."""
    async def event_generator():
        async for chunk in stream_ai_feedback(payload.question, payload.answer):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = InterviewSession(
        user_id=current_user.id,
        session_type=payload.session_type,
        topic=payload.topic,
        difficulty=payload.difficulty,
        role=payload.role,
        transcript=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def complete_session(session_id: str, payload: SessionCompleteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    session.score = payload.score
    session.answered = payload.answered
    session.total_questions = payload.total_questions
    session.transcript = payload.transcript
    session.summary = payload.summary or f"Completed {payload.answered} of {payload.total_questions} questions."
    session.completed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(session)
    return session


@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
        .limit(50)
        .all()
    )
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session
