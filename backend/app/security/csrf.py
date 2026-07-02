from fastapi import Depends, Header, HTTPException, status

from app.models.session import SessionRecord
from app.security.session import get_current_session
from app.security.tokens import tokens_match


def require_csrf_token(
    session_record: SessionRecord = Depends(get_current_session), x_csrf_token: str | None = Header(default=None)
) -> SessionRecord:
    if not x_csrf_token or not tokens_match(x_csrf_token, session_record.csrf_token_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
    return session_record
