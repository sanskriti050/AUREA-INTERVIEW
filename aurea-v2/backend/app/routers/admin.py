from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.question import QuizQuestion
from app.models.user import User

router = APIRouter(prefix="/admin/questions", tags=["Question administration"])


class QuestionPayload(BaseModel):
    topic: str = Field(min_length=2, max_length=100)
    difficulty: str = Field(pattern="^(Easy|Medium|Hard)$")
    question: str = Field(min_length=5, max_length=5000)
    options: list[str] = Field(min_length=2, max_length=8)
    correct_index: int = Field(ge=0)
    is_active: bool = True

    @field_validator("options")
    @classmethod
    def valid_options(cls, options: list[str]) -> list[str]:
        if any(not option.strip() for option in options):
            raise ValueError("Options cannot be blank")
        return [option.strip() for option in options]

    def model_post_init(self, __context):
        if self.correct_index >= len(self.options):
            raise ValueError("correct_index must refer to an option")


def serialize(question: QuizQuestion) -> dict:
    return {"id": question.id, "topic": question.topic, "difficulty": question.difficulty,
            "question": question.question, "options": question.options,
            "correct_index": question.correct_index, "is_active": question.is_active}


@router.get("")
def list_questions(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return {"questions": [serialize(q) for q in db.query(QuizQuestion).order_by(QuizQuestion.created_at.desc()).all()]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    question = QuizQuestion(**payload.model_dump())
    db.add(question); db.commit(); db.refresh(question)
    return serialize(question)


@router.put("/{question_id}")
def update_question(question_id: str, payload: QuestionPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    question = db.get(QuizQuestion, question_id)
    if not question: raise HTTPException(status_code=404, detail="Question not found.")
    for key, value in payload.model_dump().items(): setattr(question, key, value)
    db.commit(); db.refresh(question)
    return serialize(question)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    question = db.get(QuizQuestion, question_id)
    if not question: raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(question); db.commit()
