from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeAnalysisResponse(BaseModel):
    id: str
    filename: str
    name: str
    email: Optional[str]
    github: Optional[str]
    linkedin: Optional[str]
    skills: List[str]
    top_role: str
    role_matches: List[Dict[str, Any]]
    missing_skills: List[str]
    tips: List[str]
    roadmap: List[Dict[str, Any]]
    sections: Dict[str, bool]
    quantified_bullets: int
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class JDMatchRequest(BaseModel):
    job_description: str


class JDMatchResponse(BaseModel):
    match_score: int          # 0-100
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
