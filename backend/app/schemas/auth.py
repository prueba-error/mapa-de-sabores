from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserRegisterRequest(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class UserLoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_REGEX)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
