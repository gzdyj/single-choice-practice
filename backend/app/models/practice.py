from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from ..database import Base


class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    user_answer = Column(String(1), nullable=False)   # A / B / C / D
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
