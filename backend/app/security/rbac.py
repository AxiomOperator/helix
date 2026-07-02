ALLOWED_ROLES = {"viewer", "operator", "admin", "break_glass_admin"}
from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.security.session import get_current_user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin", "break_glass_admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user
