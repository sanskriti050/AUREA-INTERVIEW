from pydantic import BaseModel, field_validator
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

    @field_validator("job_description")
    @classmethod
    def require_meaningful_job_description(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 200 or len(cleaned.split()) < 30:
            raise ValueError("Paste a complete job description (at least 30 words). A title such as 'ML job' cannot be matched reliably.")
        return cleaned


class JDMatchResponse(BaseModel):
    match_score: int          # 0-100
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
    semantic_score: Optional[int] = None
    match_method: Optional[str] = None
    skill_coverage: Optional[int] = None
    matched_skill_count: Optional[int] = None
    required_skill_count: Optional[int] = None
    analysis_summary: Optional[str] = None
