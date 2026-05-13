import random
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..models.exam import Exam, ExamQuestion, ExamAttempt, ExamAnswer
from ..models.question import Question
from ..models.user import User
from ..schemas.exam import (
    ExamResponse,
    ExamQuestionItem,
    ExamStartResponse,
    ExamResultResponse,
    ExamAnswerDetail,
    ExamAttemptItem,
)


def _exam_to_response(exam: Exam) -> ExamResponse:
    """Convert Exam model to ExamResponse schema."""
    return ExamResponse(
        id=exam.id,
        title=exam.title,
        description=exam.description or "",
        category_id=exam.category_id,
        category_name=exam.category.name if exam.category else None,
        difficulty=exam.difficulty,
        question_count=exam.question_count,
        time_limit_minutes=exam.time_limit_minutes,
        passing_score=exam.passing_score,
        shuffle_questions=exam.shuffle_questions,
        created_by=exam.created_by,
        creator_name=exam.creator.nickname if exam.creator else None,
        is_active=exam.is_active,
        created_at=exam.created_at,
        updated_at=exam.updated_at,
    )


# ── Exam CRUD ──


def get_exam_list(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    keyword: str | None = None,
    show_all: bool = False,  # admin sees all; others see active only
) -> tuple[list[ExamResponse], int]:
    query = db.query(Exam)
    if not show_all:
        query = query.filter(Exam.is_active == True)
    if category_id is not None:
        query = query.filter(Exam.category_id == category_id)
    if keyword:
        query = query.filter(Exam.title.ilike(f"%{keyword}%"))
    query = query.order_by(Exam.created_at.desc())
    total = query.count()
    offset = (page - 1) * page_size
    exams = query.offset(offset).limit(page_size).all()
    return [_exam_to_response(e) for e in exams], total


def get_exam_by_id(db: Session, exam_id: int) -> Exam | None:
    return db.query(Exam).filter(Exam.id == exam_id).first()


def create_exam(db: Session, data, user_id: int) -> Exam:
    """Create exam - support both manual question selection and random auto-pick."""
    # If question_ids is provided, use actual count for the exam record
    if data.question_ids and len(data.question_ids) > 0:
        actual_question_count = len(data.question_ids)
    else:
        actual_question_count = data.question_count

    exam = Exam(
        title=data.title,
        description=data.description or "",
        category_id=data.category_id,
        difficulty=data.difficulty,
        question_count=actual_question_count,
        time_limit_minutes=data.time_limit_minutes,
        passing_score=data.passing_score,
        shuffle_questions=data.shuffle_questions,
        created_by=user_id,
    )
    db.add(exam)
    db.flush()  # get exam.id

    # Manual selection mode
    if data.question_ids and len(data.question_ids) > 0:
        selected = db.query(Question).filter(Question.id.in_(data.question_ids)).all()
        if len(selected) != len(data.question_ids):
            found_ids = {q.id for q in selected}
            missing = [qid for qid in data.question_ids if qid not in found_ids]
            raise ValueError(f"部分题目不存在: {missing}")
    else:
        # Auto-random selection matching criteria
        q_query = db.query(Question)
        if data.category_id:
            q_query = q_query.filter(Question.category_id == data.category_id)
        if data.difficulty:
            q_query = q_query.filter(Question.difficulty == data.difficulty)

        all_questions = q_query.all()
        if len(all_questions) < data.question_count:
            # Not enough questions: use all available
            selected = all_questions
        else:
            selected = random.sample(all_questions, data.question_count)

    # Create ExamQuestion records
    for idx, q in enumerate(selected):
        eq = ExamQuestion(
            exam_id=exam.id,
            question_id=q.id,
            sort_order=idx,
        )
        db.add(eq)

    db.commit()
    db.refresh(exam)
    return exam


def update_exam(db: Session, exam_id: int, data) -> Exam:
    exam = get_exam_by_id(db, exam_id)
    if not exam:
        raise ValueError("考试不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exam, key, value)
    exam.updated_at = datetime.utcnow()

    # If question_count changed, re-select questions
    if "question_count" in update_data or "category_id" in update_data or "difficulty" in update_data:
        # Remove existing exam_questions
        db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete()
        # Re-pick
        q_query = db.query(Question)
        if exam.category_id:
            q_query = q_query.filter(Question.category_id == exam.category_id)
        if exam.difficulty:
            q_query = q_query.filter(Question.difficulty == exam.difficulty)
        all_questions = q_query.all()
        count = min(exam.question_count, len(all_questions))
        selected = random.sample(all_questions, count) if count < len(all_questions) else all_questions
        for idx, q in enumerate(selected):
            eq = ExamQuestion(exam_id=exam.id, question_id=q.id, sort_order=idx)
            db.add(eq)

    db.commit()
    db.refresh(exam)
    return exam


def delete_exam(db: Session, exam_id: int):
    exam = get_exam_by_id(db, exam_id)
    if not exam:
        raise ValueError("考试不存在")
    # Due to cascade settings, related ExamQuestion and ExamAttempt/Answer are NOT auto-deleted.
    # Manually clean up.
    db.query(ExamAnswer).filter(
        ExamAnswer.attempt_id.in_(
            db.query(ExamAttempt.id).filter(ExamAttempt.exam_id == exam_id)
        )
    ).delete(synchronize_session=False)
    db.query(ExamAttempt).filter(ExamAttempt.exam_id == exam_id).delete()
    db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete()
    db.delete(exam)
    db.commit()


# ── Exam Questions ──


def get_exam_questions(db: Session, exam_id: int) -> list[ExamQuestionItem]:
    eqs = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.exam_id == exam_id)
        .order_by(ExamQuestion.sort_order)
        .all()
    )
    result = []
    for eq in eqs:
        q = eq.question
        result.append(ExamQuestionItem(
            id=eq.id,
            question_id=q.id,
            sort_order=eq.sort_order,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty,
            subject=q.subject,
        ))
    return result


# ── Exam Taking ──


def start_exam(db: Session, exam_id: int, user_id: int) -> ExamStartResponse:
    """Start an exam attempt. Return questions (shuffled if configured)."""
    exam = get_exam_by_id(db, exam_id)
    if not exam:
        raise ValueError("考试不存在")
    if not exam.is_active:
        raise ValueError("考试已关闭")

    # Check for in-progress attempt
    existing = (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.user_id == user_id,
            ExamAttempt.status == "in_progress",
        )
        .first()
    )
    if existing:
        raise ValueError("你已经有正在进行中的考试，请先提交或等待超时")

    # Fetch exam questions
    eqs = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.exam_id == exam_id)
        .options(joinedload(ExamQuestion.question))
        .all()
    )
    if not eqs:
        raise ValueError("该考试没有题目")

    # Shuffle if configured
    if exam.shuffle_questions:
        eqs = list(eqs)
        random.shuffle(eqs)

    # Create attempt
    attempt = ExamAttempt(
        exam_id=exam_id,
        user_id=user_id,
        total_questions=len(eqs),
        status="in_progress",
    )
    db.add(attempt)
    db.flush()

    # Create empty answer records for all questions
    for eq in eqs:
        answer = ExamAnswer(
            attempt_id=attempt.id,
            question_id=eq.question_id,
        )
        db.add(answer)

    db.commit()
    db.refresh(attempt)

    # Build question list (without correct_answer)
    questions = []
    for eq in eqs:
        q = eq.question
        questions.append(ExamQuestionItem(
            id=eq.id,
            question_id=q.id,
            sort_order=0,  # order is determined by shuffled list
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty,
            subject=q.subject,
        ))

    return ExamStartResponse(
        attempt_id=attempt.id,
        exam_id=exam.id,
        exam_title=exam.title,
        exam_description=exam.description or "",
        time_limit_minutes=exam.time_limit_minutes,
        passing_score=exam.passing_score,
        started_at=attempt.started_at,
        questions=questions,
        total_questions=len(questions),
    )


def submit_exam(db: Session, attempt_id: int, user_id: int, answers_data: list) -> ExamResultResponse:
    """Submit an exam attempt, grade answers, and return result."""
    attempt = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == user_id)
        .first()
    )
    if not attempt:
        raise ValueError("考试记录不存在")
    if attempt.status != "in_progress":
        raise ValueError("考试已提交，无法重复提交")

    # Check time limit
    exam = attempt.exam
    elapsed = (datetime.utcnow() - attempt.started_at).total_seconds()
    time_limit_seconds = exam.time_limit_minutes * 60
    if elapsed > time_limit_seconds:
        attempt.status = "timed_out"
        db.commit()
        raise ValueError("考试超时，无法提交")

    # Build answer lookup
    answer_map = {a.question_id: a.selected_answer for a in answers_data}

    # Grade answers
    db_answers = (
        db.query(ExamAnswer)
        .filter(ExamAnswer.attempt_id == attempt_id)
        .all()
    )
    correct_count = 0
    now = datetime.utcnow()

    for ans in db_answers:
        question = ans.question
        selected = answer_map.get(question.id)
        ans.selected_answer = selected
        ans.answered_at = now
        if selected:
            is_correct = selected.upper() == question.correct_answer
            ans.is_correct = is_correct
            if is_correct:
                correct_count += 1
        else:
            ans.is_correct = False

    score = round((correct_count / attempt.total_questions) * 100) if attempt.total_questions > 0 else 0

    attempt.correct_count = correct_count
    attempt.score = score
    attempt.submitted_at = now
    attempt.status = "submitted"
    db.commit()
    db.refresh(attempt)

    return _build_result(attempt)


def _build_result(attempt: ExamAttempt) -> ExamResultResponse:
    """Build result response from a submitted/graded attempt."""
    exam = attempt.exam
    time_used = None
    if attempt.submitted_at:
        time_used = int((attempt.submitted_at - attempt.started_at).total_seconds())

    answers = []
    for ans in attempt.answers:
        q = ans.question
        answers.append(ExamAnswerDetail(
            question_id=q.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty,
            subject=q.subject,
            selected_answer=ans.selected_answer,
            correct_answer=q.correct_answer,
            is_correct=ans.is_correct,
        ))

    return ExamResultResponse(
        attempt_id=attempt.id,
        exam_id=exam.id,
        exam_title=exam.title,
        score=attempt.score or 0,
        correct_count=attempt.correct_count or 0,
        total_questions=attempt.total_questions,
        passing_score=exam.passing_score,
        passed=(attempt.score or 0) >= exam.passing_score,
        status=attempt.status,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        time_used_seconds=time_used,
        answers=answers,
    )


def get_exam_result(db: Session, attempt_id: int, user_id: int) -> ExamResultResponse:
    """Get result for a specific attempt."""
    attempt = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == user_id)
        .first()
    )
    if not attempt:
        raise ValueError("考试记录不存在")
    return _build_result(attempt)


def get_user_attempts(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ExamAttemptItem], int]:
    """Get exam history for a user."""
    query = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.user_id == user_id)
        .order_by(ExamAttempt.started_at.desc())
    )
    total = query.count()
    offset = (page - 1) * page_size
    attempts = query.offset(offset).limit(page_size).all()

    items = []
    for a in attempts:
        exam = a.exam
        items.append(ExamAttemptItem(
            attempt_id=a.id,
            exam_id=exam.id,
            exam_title=exam.title,
            score=a.score,
            correct_count=a.correct_count,
            total_questions=a.total_questions,
            passing_score=exam.passing_score,
            passed=(a.score or 0) >= exam.passing_score if a.score is not None else None,
            status=a.status,
            started_at=a.started_at,
            submitted_at=a.submitted_at,
        ))
    return items, total
