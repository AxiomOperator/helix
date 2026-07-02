from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserRead
from app.security.session import get_current_user

router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        role=current_user.role,
    )
