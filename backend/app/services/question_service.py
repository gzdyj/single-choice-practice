from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.question import Question
from ..schemas.question import QuestionCreate, QuestionUpdate


def get_question_by_id(db: Session, question_id: int) -> Question | None:
    return db.query(Question).filter(Question.id == question_id).first()


def get_question_list(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    subject: str | None = None,
    difficulty: str | None = None,
    keyword: str | None = None,
    category_id: int | None = None,
) -> tuple[list[Question], int]:
    query = db.query(Question)
    if subject:
        query = query.filter(Question.subject == subject)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if keyword:
        keyword_filter = or_(
            Question.question_text.contains(keyword),
            Question.subject.contains(keyword),
        )
        query = query.filter(keyword_filter)
    if category_id is not None:
        query = query.filter(Question.category_id == category_id)
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Question.id).offset(offset).limit(page_size).all()
    return items, total


def create_question(db: Session, data: QuestionCreate, user_id: int) -> Question:
    question = Question(
        category_id=data.category_id,
        subject=data.subject,
        difficulty=data.difficulty,
        question_text=data.question_text,
        option_a=data.option_a,
        option_b=data.option_b,
        option_c=data.option_c,
        option_d=data.option_d,
        correct_answer=data.correct_answer,
        explanation=data.explanation,
        created_by=user_id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update_question(db: Session, question_id: int, data: QuestionUpdate) -> Question:
    question = get_question_by_id(db, question_id)
    if not question:
        raise ValueError("题目不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: int) -> None:
    question = get_question_by_id(db, question_id)
    if not question:
        raise ValueError("题目不存在")
    db.delete(question)
    db.commit()


def get_all_subjects(db: Session) -> list[str]:
    results = db.query(Question.subject).distinct().order_by(Question.subject).all()
    return [r[0] for r in results if r[0]]
