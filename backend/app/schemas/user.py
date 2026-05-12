from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)
    nickname: str = Field(default="", max_length=64)
    role: str = Field(default="student", pattern="^(admin|teacher|student)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)
    nickname: str = Field(default="", max_length=64)
    role: str = Field(default="student", pattern="^(admin|teacher|student)$")
    is_active: bool = True


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=64)
    role: Optional[str] = Field(default=None, pattern="^(admin|teacher|student)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=4, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=4, max_length=128)
