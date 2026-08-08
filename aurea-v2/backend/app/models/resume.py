from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, default=list)           # ["Python", "SQL", ...]
    top_role = Column(String(100), nullable=True)
    role_matches = Column(JSON, default=list)     # [{role, score, matched, missing}]
    tips = Column(JSON, default=list)
    roadmap = Column(JSON, default=list)
    sections = Column(JSON, default=dict)
    quantified_bullets = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    email_detected = Column(String, nullable=True)
    github_detected = Column(String, nullable=True)
    linkedin_detected = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="resume")
