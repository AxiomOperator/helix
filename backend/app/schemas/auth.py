from pydantic import BaseModel

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class LoginResponse(BaseModel):
    user: UserRead


class CsrfResponse(BaseModel):
    csrf_token: str


class StatusResponse(BaseModel):
    status: str
