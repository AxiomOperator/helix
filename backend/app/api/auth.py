from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.session import SessionRecord
from app.schemas.auth import CsrfResponse, LoginRequest, LoginResponse, StatusResponse
from app.schemas.user import UserRead
from app.security.csrf import require_csrf_token
from app.security.session import get_current_session
from app.services.audit_service import write_audit_event
from app.services.auth_service import authenticate_user, create_session, get_raw_csrf_token, revoke_session

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_read(user) -> UserRead:
    return UserRead(
        id=str(user.id),
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
    )


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username_or_email, payload.password)
    if not user:
        write_audit_event(
            db,
            action="auth.login.failed",
            result="failure",
            request=request,
            metadata={"username_or_email": payload.username_or_email},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    _session_record, session_token, _csrf_token = create_session(db, user, request)
    write_audit_event(
        db,
        action="auth.login.success",
        result="success",
        request=request,
        actor_id=user.id,
        metadata={"username_or_email": payload.username_or_email},
    )
    db.commit()

    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
        max_age=settings.session_expire_hours * 60 * 60,
    )
    return LoginResponse(user=_user_read(user))


@router.get("/csrf", response_model=CsrfResponse)
async def csrf_token(request: Request, session_record: SessionRecord = Depends(get_current_session)):
    settings = get_settings()
    raw_session_token = request.cookies.get(settings.session_cookie_name)
    if not raw_session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return CsrfResponse(csrf_token=get_raw_csrf_token(raw_session_token))


@router.post("/logout", response_model=StatusResponse)
async def logout(
    request: Request,
    response: Response,
    session_record: SessionRecord = Depends(require_csrf_token),
    db: Session = Depends(get_db),
):
    attached_session = db.merge(session_record)
    revoke_session(db, attached_session)
    write_audit_event(
        db,
        action="auth.logout",
        result="success",
        request=request,
        actor_id=attached_session.user_id,
        metadata={"session_id": str(attached_session.id)},
    )
    db.commit()

    settings = get_settings()
    response.delete_cookie(settings.session_cookie_name, path="/", samesite="lax", secure=settings.session_cookie_secure)
    return StatusResponse(status="ok")
