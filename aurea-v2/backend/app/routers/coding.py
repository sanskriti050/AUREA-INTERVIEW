from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.coding_engine import LANGUAGES, TOPICS, DIFFICULTIES, list_problems, starter, review_code_with_ai, PROBLEMS
from app.services.judge0 import execute_code

router = APIRouter(prefix="/coding", tags=["Coding"])


class CodeReviewRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    explanation: Optional[str] = ""


class CodeExecuteRequest(BaseModel):
    language: str
    code: str
    stdin: Optional[str] = ""


@router.get("/languages")
def get_languages():
    return {"languages": LANGUAGES}


@router.get("/topics")
def get_topics():
    return {"topics": TOPICS}


@router.get("/difficulties")
def get_difficulties():
    return {"difficulties": DIFFICULTIES}


@router.get("/problems/{topic}/{difficulty}")
def get_problems(topic: str, difficulty: str, count: int = 10):
    problems = list_problems(topic, difficulty)
    if not problems:
        raise HTTPException(status_code=404, detail="No problems found.")
    import random
    if count < len(problems):
        problems = random.sample(problems, count)
    return {"problems": problems}


@router.get("/starter/{problem_id}/{language}")
def get_starter(problem_id: str, language: str):
    problem = next((p for p in PROBLEMS if p["id"] == problem_id), None)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    if language not in LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language.")
    return {"starter": starter(problem, language), "problem": problem}


@router.post("/review")
async def review(
    payload: CodeReviewRequest,
    current_user: User = Depends(get_current_user),
):
    problem = next((p for p in PROBLEMS if p["id"] == payload.problem_id), None)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    if payload.language not in LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language.")

    result = await review_code_with_ai(problem, payload.language, payload.code, payload.explanation)
    return result


@router.post("/execute")
async def execute(
    payload: CodeExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    """Run code via Judge0 API and return stdout/stderr."""
    result = await execute_code(payload.language, payload.code, payload.stdin)
    return result
