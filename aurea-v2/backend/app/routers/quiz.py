from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.progress import ProgressEvent, EventType
from app.models.question import QuizQuestion
from app.services.question_bank import quiz_topics, quiz_difficulties, quiz_questions

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.get("/topics")
def get_topics():
    return {"topics": quiz_topics()}


@router.get("/difficulties/{topic}")
def get_difficulties(topic: str):
    diffs = quiz_difficulties(topic)
    if not diffs:
        raise HTTPException(status_code=404, detail="Topic not found.")
    return {"difficulties": diffs}


@router.get("/questions/{topic}/{difficulty}")
def get_questions(topic: str, difficulty: str, count: int = 20, db: Session = Depends(get_db)):
    managed = db.query(QuizQuestion).filter(
        QuizQuestion.topic == topic, QuizQuestion.difficulty == difficulty, QuizQuestion.is_active.is_(True)
    ).all()
    questions = ([{"id": q.id, "question": q.question, "options": q.options, "correct": q.correct_index}
                  for q in managed] or quiz_questions(topic, difficulty))
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this combination.")
    import random
    if count < len(questions):
        questions = random.sample(questions, count)
    # Strip correct answer from response — evaluated server-side
    safe = [{k: v for k, v in q.items() if k != "correct"} for q in questions]
    return {"questions": safe, "total": len(safe)}


@router.post("/submit/{topic}/{difficulty}")
def submit_answers(
    topic: str,
    difficulty: str,
    answers: dict,   # {question_id: selected_index}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate submitted answers server-side and record progress.
    Body: {"answers": {"q-id-1": 2, "q-id-2": 0, ...}}
    """
    managed = db.query(QuizQuestion).filter(
        QuizQuestion.topic == topic, QuizQuestion.difficulty == difficulty, QuizQuestion.is_active.is_(True)
    ).all()
    questions = ([{"id": q.id, "question": q.question, "options": q.options, "correct": q.correct_index}
                  for q in managed] or quiz_questions(topic, difficulty))
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found.")

    q_map = {q["id"]: q for q in questions}
    submitted = answers.get("answers", {})
    results = []
    correct_count = 0

    for q in questions:
        qid = q["id"]
        selected = submitted.get(qid)
        correct = q["correct"]
        is_correct = selected == correct
        if is_correct:
            correct_count += 1
        results.append({
            "id": qid,
            "question": q["question"],
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
            "correct_option": q["options"][correct],
        })

        # Record each answer as a progress event
        event = ProgressEvent(
            user_id=current_user.id,
            event_type=EventType.quiz_answer,
            topic=topic,
            difficulty=difficulty,
            score=100.0 if is_correct else 0.0,
            payload={"question_id": qid, "correct": is_correct},
        )
        db.add(event)

    db.commit()
    score = round(correct_count / len(questions) * 100) if questions else 0
    return {
        "score": score,
        "correct": correct_count,
        "total": len(questions),
        "results": results,
    }
