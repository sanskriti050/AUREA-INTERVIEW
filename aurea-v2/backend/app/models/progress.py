from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum as py_enum
from app.core.database import Base


class EventType(str, py_enum.Enum):
    quiz_answer = "quiz_answer"
    theory_evaluated = "theory_evaluated"
    code_review = "code_review"
    mock_completed = "mock_completed"


class ProgressEvent(Base):
    __tablename__ = "progress_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)
    score = Column(Float, nullable=True)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="progress_events")
