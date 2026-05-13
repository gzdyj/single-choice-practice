from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.exam import (
    ExamCreate, ExamUpdate, ExamResponse, ExamListResponse,
    ExamQuestionItem,
    ExamStartResponse, ExamSubmitRequest, ExamResultResponse,
    ExamAttemptListResponse,
)
from ..services import exam_service
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/exams", tags=["考试模式"])


# ── Exam CRUD (admin/teacher) ──


@router.get("", response_model=ExamListResponse)
def list_exams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int = Query(None, description="按分类筛选"),
    keyword: str = Query(None, description="按标题搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取考试列表（学生只看已发布的，管理员看全部）"""
    show_all = current_user.role in ("admin", "teacher")
    items, total = exam_service.get_exam_list(db, page, page_size, category_id, keyword, show_all)
    return ExamListResponse(total=total, items=items)


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(
    data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """创建考试（自动按条件随机选题）"""
    try:
        exam = exam_service.create_exam(db, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return exam_service._exam_to_response(exam)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取考试详情"""
    exam = exam_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")
    if not exam.is_active and current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")
    return exam_service._exam_to_response(exam)


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """更新考试"""
    try:
        exam = exam_service.update_exam(db, exam_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return exam_service._exam_to_response(exam)


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """删除考试"""
    try:
        exam_service.delete_exam(db, exam_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{exam_id}/questions", response_model=list[ExamQuestionItem])
def list_exam_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看考试包含的题目列表"""
    exam = exam_service.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="考试不存在")
    return exam_service.get_exam_questions(db, exam_id)


# ── Exam Taking (student) ──


@router.post("/{exam_id}/start", response_model=ExamStartResponse)
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """开始考试"""
    try:
        return exam_service.start_exam(db, exam_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{exam_id}/submit", response_model=ExamResultResponse)
def submit_exam(
    exam_id: int,
    data: ExamSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """提交考试答案并自动评分"""
    # Find the user's in-progress attempt for this exam
    from ..models.exam import ExamAttempt
    attempt = (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.status == "in_progress",
        )
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有进行中的考试")
    try:
        return exam_service.submit_exam(db, attempt.id, current_user.id, data.answers)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/attempt/{attempt_id}/result", response_model=ExamResultResponse)
def get_exam_result(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """获取考试结果"""
    try:
        return exam_service.get_exam_result(db, attempt_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Exam History ──


@router.get("/attempts/mine", response_model=ExamAttemptListResponse)
def my_exam_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student", "admin", "teacher")),
):
    """获取我的考试记录"""
    items, total = exam_service.get_user_attempts(db, current_user.id, page, page_size)
    return ExamAttemptListResponse(total=total, items=items)
