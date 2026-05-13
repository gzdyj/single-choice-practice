from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Exam CRUD Schemas ──

class ExamCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="考试标题")
    description: str = Field("", max_length=2000, description="考试说明")
    category_id: Optional[int] = Field(None, description="限定分类")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$", description="限定难度")
    question_count: int = Field(10, ge=1, le=200, description="题目数量")
    time_limit_minutes: int = Field(30, ge=1, le=300, description="时间限制（分钟）")
    passing_score: int = Field(60, ge=0, le=100, description="及格分数（百分比）")
    shuffle_questions: bool = Field(True, description="是否随机打乱题目顺序")
    question_ids: Optional[list[int]] = Field(None, description="手动指定题目ID列表，优先级高于随机选题")


class ExamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category_id: Optional[int] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    question_count: Optional[int] = Field(None, ge=1, le=200)
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    shuffle_questions: Optional[bool] = None
    is_active: Optional[bool] = None


class ExamResponse(BaseModel):
    id: int
    title: str
    description: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    difficulty: Optional[str] = None
    question_count: int
    time_limit_minutes: int
    passing_score: int
    shuffle_questions: bool
    created_by: int
    creator_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExamListResponse(BaseModel):
    total: int
    items: list[ExamResponse]


# ── Exam Taking Schemas ──

class ExamQuestionItem(BaseModel):
    """考试中一道题目的展示（不含正确答案）"""
    id: int
    question_id: int
    sort_order: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    subject: Optional[str] = None


class ExamStartResponse(BaseModel):
    attempt_id: int
    exam_id: int
    exam_title: str
    exam_description: str
    time_limit_minutes: int
    passing_score: int
    started_at: datetime
    questions: list[ExamQuestionItem]
    total_questions: int


class AnswerSubmitItem(BaseModel):
    question_id: int
    selected_answer: Optional[str] = Field(None, pattern="^[A-D]$")


class ExamSubmitRequest(BaseModel):
    answers: list[AnswerSubmitItem] = Field(..., description="所有题目的作答结果")


class ExamAnswerDetail(BaseModel):
    question_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    subject: Optional[str] = None
    selected_answer: Optional[str] = None
    correct_answer: str
    is_correct: Optional[bool] = None


class ExamResultResponse(BaseModel):
    attempt_id: int
    exam_id: int
    exam_title: str
    score: int  # 0-100
    correct_count: int
    total_questions: int
    passing_score: int
    passed: bool
    status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_used_seconds: Optional[int] = None
    answers: list[ExamAnswerDetail]


class ExamAttemptItem(BaseModel):
    """考试记录列表项"""
    attempt_id: int
    exam_id: int
    exam_title: str
    score: Optional[int] = None
    correct_count: Optional[int] = None
    total_questions: int
    passing_score: int
    passed: Optional[bool] = None
    status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExamAttemptListResponse(BaseModel):
    total: int
    items: list[ExamAttemptItem]
