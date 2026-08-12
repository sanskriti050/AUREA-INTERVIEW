"""FastAPI dependencies — supports both httpOnly cookie auth and Bearer token auth.

Cookie auth is the secure default (tokens not accessible via JavaScript).
Bearer token auth is kept as fallback for API clients and the interactive docs.
"""
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    # Cookie-based auth (httpOnly — not accessible to JavaScript)
    access_token_cookie: Optional[str] = Cookie(default=None, alias="access_token"),
    # Bearer token fallback (for API clients / Swagger docs)
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    # Prefer cookie; fall back to Authorization header
    token: Optional[str] = None
    if access_token_cookie:
        token = access_token_cookie
    elif credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow question management only for explicitly configured administrator emails."""
    if current_user.email.lower() not in settings.admin_emails:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return current_user
