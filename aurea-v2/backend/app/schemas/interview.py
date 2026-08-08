from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class TheoryQuestionRequest(BaseModel):
    role: str
    topic: str
    difficulty: str
    skills: Optional[List[str]] = None
    count: int = 10


class EvaluateAnswerRequest(BaseModel):
    question: str
    answer: str
    topic: str
    difficulty: str


class EvaluateAnswerResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    score: int
    verdict: str
    strengths: List[str]
    gaps: List[str]
    tips: List[str]
    sample: str
    model_answer: Dict[str, Any]


class AIFeedbackRequest(BaseModel):
    question: str
    answer: str


class SessionCreateRequest(BaseModel):
    session_type: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    role: Optional[str] = None


class SessionCompleteRequest(BaseModel):
    score: float
    answered: int
    total_questions: int
    transcript: List[Dict[str, Any]]
    summary: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    session_type: str
    topic: Optional[str]
    difficulty: Optional[str]
    role: Optional[str]
    score: Optional[float]
    total_questions: int
    answered: int
    transcript: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
