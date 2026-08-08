from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.ai_service import stream_chat, PromptSafetyError, _sanitize
import json

router = APIRouter(prefix="/chat", tags=["Chat"])


class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    resume_context: Optional[str] = None


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream AI chat responses via Server-Sent Events."""
    if not payload.messages or len(payload.messages) > 16:
        raise HTTPException(status_code=422, detail="Send between 1 and 16 messages.")
    if any(message.role not in {"user", "assistant"} for message in payload.messages):
        raise HTTPException(status_code=422, detail="Only user and assistant message roles are allowed.")
    try:
        messages = [{"role": m.role, "content": _sanitize(m.content)} for m in payload.messages]
        resume_context = _sanitize(payload.resume_context, 3000) if payload.resume_context else None
    except PromptSafetyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    async def event_generator():
        async for chunk in stream_chat(messages, resume_context=resume_context):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
