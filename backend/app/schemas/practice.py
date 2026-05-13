from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .question import QuestionResponse


class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str = Field(..., pattern="^[A-D]$")


class PracticeResult(BaseModel):
    question: QuestionResponse
    user_answer: str
    is_correct: bool


class PracticeHistoryItem(BaseModel):
    id: int
    question_id: int
    question_text: str
    category_id: Optional[int] = None
    subject: str
    difficulty: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PracticeHistoryResponse(BaseModel):
    total: int
    items: list[PracticeHistoryItem]


class PracticeStats(BaseModel):
    total_attempts: int
    correct_count: int
    wrong_count: int
    accuracy: float  # 0-100
