from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    difficulty = Column(String(10), nullable=True)  # easy / medium / hard / null
    question_count = Column(Integer, nullable=False, default=10)
    time_limit_minutes = Column(Integer, nullable=False, default=30)
    passing_score = Column(Integer, nullable=False, default=60)  # 0-100
    shuffle_questions = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    category = relationship("Category", lazy="joined")
    creator = relationship("User", lazy="joined")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    __table_args__ = (UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),)

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    # relationships
    question = relationship("Question", lazy="joined")


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)  # 0-100
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")  # in_progress / submitted / timed_out

    # relationships
    exam = relationship("Exam", lazy="joined")
    user = relationship("User", lazy="joined")
    answers = relationship("ExamAnswer", back_populates="attempt", lazy="selectin",
                           cascade="all, delete-orphan")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(String(1), nullable=True)  # A/B/C/D, null if unanswered
    is_correct = Column(Boolean, nullable=True)
    answered_at = Column(DateTime, nullable=True)

    # relationships
    attempt = relationship("ExamAttempt", back_populates="answers")
    question = relationship("Question", lazy="joined")
