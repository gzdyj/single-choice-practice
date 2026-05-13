from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.practice import (
    AnswerSubmit, PracticeResult, PracticeHistoryResponse, PracticeStats,
)
from ..schemas.question import PracticeQuestionResponse
from ..services import practice_service
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/practice", tags=["刷题练习"])


@router.get("/random", response_model=PracticeQuestionResponse)
def get_random_question(
    category_id: int = Query(None, description="按分类筛选"),
    difficulty: str = Query(None, description="按难度筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """随机抽取一道题目（排除已答对的题目，不返回正确答案）"""
    question = practice_service.get_random_question(db, current_user.id, category_id, difficulty)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该条件下没有符合的题目！",
        )
    return PracticeQuestionResponse(
        id=question.id,
        category_id=question.category_id,
        subject=question.subject,
        difficulty=question.difficulty,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        explanation=question.explanation,
        created_by=question.created_by,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


@router.post("/submit", response_model=PracticeResult)
def submit_answer(
    data: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """提交答案并判定正误"""
    try:
        return practice_service.submit_answer(db, current_user.id, data.question_id, data.user_answer)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history", response_model=PracticeHistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    subject: str = Query(None, description="按学科筛选"),
    difficulty: str = Query(None, description="按难度筛选"),
    category_id: int = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """获取练习历史记录（分页，支持按学科/难度/分类筛选）"""
    items, total = practice_service.get_history(db, current_user.id, page, page_size, subject, difficulty, category_id)
    return PracticeHistoryResponse(total=total, items=items)


@router.get("/stats", response_model=PracticeStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """获取练习统计数据"""
    stats = practice_service.get_stats(db, current_user.id)
    return PracticeStats(**stats)
