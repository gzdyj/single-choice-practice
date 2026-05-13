from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator


def validate_password_strength(password: str) -> str:
    """Validate password strength: 8+ chars, must contain uppercase, lowercase, digit, and special char."""
    if len(password) < 8:
        raise ValueError("密码长度至少 8 位")
    if not re.search(r"[A-Z]", password):
        raise ValueError("密码必须包含至少一个大写字母")
    if not re.search(r"[a-z]", password):
        raise ValueError("密码必须包含至少一个小写字母")
    if not re.search(r"\d", password):
        raise ValueError("密码必须包含至少一个数字")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~]", password):
        raise ValueError("密码必须包含至少一个特殊字符")
    return password


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        return validate_password_strength(v)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str = Field(default="", max_length=64)
    role: str = Field(default="student", pattern="^(admin|teacher|student)$")

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        return validate_password_strength(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str = Field(default="", max_length=64)
    role: str = Field(default="student", pattern="^(admin|teacher|student)$")
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=64)
    role: Optional[str] = Field(default=None, pattern="^(admin|teacher|student)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v):
        if v is not None:
            return validate_password_strength(v)
        return v


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
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password_strength(cls, v):
        return validate_password_strength(v)
