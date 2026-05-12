from sqlalchemy.orm import Session
from sqlalchemy import not_, func

from ..models.question import Question
from ..models.practice import PracticeRecord
from ..schemas.practice import PracticeResult, PracticeHistoryItem


def get_random_question(db: Session, user_id: int) -> Question | None:
    """Get a random question that the user hasn't answered correctly before."""
    # Subquery: IDs of questions the user answered correctly
    correct_ids = (
        db.query(PracticeRecord.question_id)
        .filter(
            PracticeRecord.user_id == user_id,
            PracticeRecord.is_correct == True,
        )
        .subquery()
    )

    question = (
        db.query(Question)
        .filter(not_(Question.id.in_(correct_ids)))
        .order_by(func.random())
        .first()
    )
    return question


def submit_answer(
    db: Session,
    user_id: int,
    question_id: int,
    user_answer: str,
) -> PracticeResult:
    """Submit an answer and return the result."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError("题目不存在")

    is_correct = user_answer.upper() == question.correct_answer
    record = PracticeRecord(
        user_id=user_id,
        question_id=question_id,
        user_answer=user_answer.upper(),
        is_correct=is_correct,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PracticeResult(
        question=question,
        user_answer=user_answer.upper(),
        is_correct=is_correct,
    )


def get_history(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PracticeHistoryItem], int]:
    """Get practice history for a user."""
    query = (
        db.query(PracticeRecord, Question)
        .join(Question, PracticeRecord.question_id == Question.id)
        .filter(PracticeRecord.user_id == user_id)
        .order_by(PracticeRecord.created_at.desc())
    )
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    history_items = []
    for record, question in items:
        history_items.append(PracticeHistoryItem(
            id=record.id,
            question_id=question.id,
            question_text=question.question_text,
            subject=question.subject,
            difficulty=question.difficulty,
            user_answer=record.user_answer,
            correct_answer=question.correct_answer,
            is_correct=record.is_correct,
            created_at=record.created_at,
        ))

    return history_items, total


def get_stats(db: Session, user_id: int):
    """Get practice statistics for a user."""
    records = db.query(PracticeRecord).filter(PracticeRecord.user_id == user_id).all()
    total = len(records)
    correct = sum(1 for r in records if r.is_correct)
    wrong = total - correct
    accuracy = round((correct / total * 100), 1) if total > 0 else 0.0

    return {
        "total_attempts": total,
        "correct_count": correct,
        "wrong_count": wrong,
        "accuracy": accuracy,
    }
