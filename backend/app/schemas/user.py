from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    display_name: str | None
    role: str

    model_config = ConfigDict(from_attributes=True)
