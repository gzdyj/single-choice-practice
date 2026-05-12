from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    subject: str = Field(default="", max_length=64)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_text: str = Field(..., min_length=1)
    option_a: str = Field(..., min_length=1)
    option_b: str = Field(..., min_length=1)
    option_c: str = Field(..., min_length=1)
    option_d: str = Field(..., min_length=1)
    correct_answer: str = Field(..., pattern="^[A-D]$")
    explanation: str = Field(default="", max_length=2048)


class QuestionUpdate(BaseModel):
    subject: Optional[str] = Field(default=None, max_length=64)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = Field(default=None, pattern="^[A-D]$")
    explanation: Optional[str] = Field(default=None, max_length=2048)


class QuestionResponse(BaseModel):
    id: int
    subject: str
    difficulty: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    total: int
    items: list[QuestionResponse]
