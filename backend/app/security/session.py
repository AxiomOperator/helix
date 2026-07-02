from datetime import UTC, datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.session import SessionRecord
from app.models.user import User
from app.security.tokens import hash_token


def get_current_session(request: Request, db: Session = Depends(get_db)) -> SessionRecord:
    settings = get_settings()
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_record = db.scalar(select(SessionRecord).where(SessionRecord.session_token_hash == hash_token(raw_token)))
    now = datetime.now(UTC)
    if not session_record or session_record.revoked_at or session_record.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_record.last_seen_at = now
    db.commit()
    db.refresh(session_record)
    return session_record


def get_current_user(
    session_record: SessionRecord = Depends(get_current_session), db: Session = Depends(get_db)
) -> User:
    user = db.get(User, session_record.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
