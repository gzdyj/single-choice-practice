from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse,
)
from ..schemas.practice import PracticeHistoryResponse, PracticeHistoryItem
from ..services import question_service
from ..services.question_service import get_all_subjects
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/questions", tags=["题库管理"])


@router.get("", response_model=QuestionListResponse)
def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    subject: str = Query(None),
    difficulty: str = Query(None, regex="^(easy|medium|hard)$"),
    keyword: str = Query(None),
    category_id: int = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取题目列表（分页，支持多条件筛选，可按分类筛选）"""
    items, total = question_service.get_question_list(
        db, page, page_size, subject, difficulty, keyword, category_id
    )
    return QuestionListResponse(total=total, items=items)


@router.get("/subjects", response_model=list[str])
def list_subjects(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取所有学科分类"""
    return get_all_subjects(db)


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """创建题目（管理员/教师）"""
    return question_service.create_question(db, data, current_user.id)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取题目详情"""
    question = question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="题目不存在")
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """更新题目（管理员/教师）"""
    try:
        return question_service.update_question(db, question_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "teacher")),
):
    """删除题目（管理员/教师）"""
    try:
        question_service.delete_question(db, question_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
