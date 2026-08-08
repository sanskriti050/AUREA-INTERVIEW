from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum as py_enum
from app.core.database import Base


class SessionType(str, py_enum.Enum):
    theory = "theory"
    coding = "coding"
    quiz = "quiz"
    mock = "mock"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_type = Column(Enum(SessionType), nullable=False)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)
    role = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)
    total_questions = Column(Integer, default=0)
    answered = Column(Integer, default=0)
    transcript = Column(JSON, default=list)   # [{question, answer, score, feedback}]
    summary = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
