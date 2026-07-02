from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.session import SessionRecord
from app.models.user import User
from app.security.password import verify_password
from app.security.tokens import derive_csrf_token, generate_token, hash_token


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    identifier = username_or_email.strip()
    user = db.scalar(select(User).where(or_(User.username == identifier, User.email == identifier)))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def create_session(db: Session, user: User, request: Request) -> tuple[SessionRecord, str, str]:
    settings = get_settings()
    session_token = generate_token()
    csrf_token = derive_csrf_token(session_token)
    session_token_hash = hash_token(session_token)
    session_record = SessionRecord(
        user_id=user.id,
        session_token_hash=session_token_hash,
        csrf_token_hash=hash_token(csrf_token),
        expires_at=datetime.now(UTC) + timedelta(hours=settings.session_expire_hours),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(session_record)
    db.flush()
    return session_record, session_token, csrf_token


def get_raw_csrf_token(session_token: str) -> str:
    return derive_csrf_token(session_token)


def revoke_session(db: Session, session_record: SessionRecord) -> None:
    session_record.revoked_at = datetime.now(UTC)
    db.add(session_record)
