from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeAnalysisResponse, JDMatchRequest, JDMatchResponse
import os

from app.services.resume_parser import analyze_resume, extract_resume_text, semantic_section_detection
from app.services.semantic_matcher import semantic_match_jd, store_resume_embedding

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed = {".pdf", ".docx", ".txt"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Upload a PDF, DOCX, or TXT file.")

    try:
        file_content = await file.read()
        raw_text = extract_resume_text(file_content, filename=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    profile = analyze_resume(raw_text)
    profile["sections"] = await semantic_section_detection(raw_text, profile["sections"])

    # Upsert — one resume per user
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        resume = Resume(user_id=current_user.id)
        db.add(resume)

    resume.filename = file.filename
    resume.raw_text = raw_text
    resume.skills = profile["skills"]
    resume.top_role = profile["top_role"]
    resume.role_matches = profile["role_matches"]
    resume.tips = profile["tips"]
    resume.roadmap = profile["roadmap"]
    resume.sections = profile["sections"]
    resume.quantified_bullets = profile["quantified_bullets"]
    resume.word_count = profile["word_count"]
    resume.email_detected = profile["email"]
    resume.github_detected = profile["github"]
    resume.linkedin_detected = profile["linkedin"]

    db.commit()
    db.refresh(resume)
    await store_resume_embedding(db, resume.id, raw_text)

    return ResumeAnalysisResponse(
        id=resume.id,
        filename=resume.filename,
        name=profile["name"],
        email=profile["email"],
        github=profile["github"],
        linkedin=profile["linkedin"],
        skills=resume.skills,
        top_role=resume.top_role,
        role_matches=resume.role_matches,
        missing_skills=profile["missing_skills"],
        tips=resume.tips,
        roadmap=resume.roadmap,
        sections=resume.sections,
        quantified_bullets=resume.quantified_bullets,
        word_count=resume.word_count,
        created_at=resume.created_at,
    )


@router.get("/me", response_model=ResumeAnalysisResponse)
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded yet.")

    profile = analyze_resume(resume.raw_text)
    return ResumeAnalysisResponse(
        id=resume.id,
        filename=resume.filename,
        name=profile["name"],
        email=profile["email"],
        github=profile["github"],
        linkedin=profile["linkedin"],
        skills=resume.skills,
        top_role=resume.top_role,
        role_matches=resume.role_matches,
        missing_skills=profile["missing_skills"],
        tips=resume.tips,
        roadmap=resume.roadmap,
        sections=resume.sections,
        quantified_bullets=resume.quantified_bullets,
        word_count=resume.word_count,
        created_at=resume.created_at,
    )


@router.post("/reanalyze")
async def reanalyze_saved_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-run heading and semantic section detection without requiring a new upload."""
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Upload a resume first.")
    profile = analyze_resume(resume.raw_text)
    resume.sections = await semantic_section_detection(resume.raw_text, profile["sections"])
    db.commit()
    await store_resume_embedding(db, resume.id, resume.raw_text)
    return {"sections": resume.sections}


@router.post("/match-jd", response_model=JDMatchResponse)
async def match_job_description(
    payload: JDMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Upload your resume first.")

    result = await semantic_match_jd(db, resume.id, resume.raw_text, payload.job_description)
    return JDMatchResponse(**result)
