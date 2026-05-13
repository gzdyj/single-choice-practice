from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    subject = Column(String(64), default="")          # 学科分类（旧字段，逐步迁移至 category_id）
    difficulty = Column(String(16), default="medium")  # easy / medium / hard
    question_text = Column(Text, nullable=False)
    option_a = Column(String(512), nullable=False)
    option_b = Column(String(512), nullable=False)
    option_c = Column(String(512), nullable=False)
    option_d = Column(String(512), nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A / B / C / D
    explanation = Column(Text, default="")
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", lazy="joined")
