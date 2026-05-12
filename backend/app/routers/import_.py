from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.question import QuestionResponse
from ..services import import_service
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/questions/import", tags=["题库导入"])


class ImportResponse(QuestionResponse):
    pass


class ImportResultSchema:
    def __init__(self, success_count: int, fail_count: int, errors: list[str], questions: list):
        self.success_count = success_count
        self.fail_count = fail_count
        self.errors = errors
        self.questions = questions


@router.post("", status_code=status.HTTP_201_CREATED)
def import_questions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
):
    """批量导入题目（支持 xlsx/csv/json 格式）"""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    content = file.file.read()
    result = import_service.import_questions(db, content, file.filename, current_user.id)

    return {
        "success_count": result.success_count,
        "fail_count": result.fail_count,
        "errors": result.errors[:50],  # 最多返回 50 条错误
        "questions": result.questions,
    }


@router.get("/formats")
def get_supported_formats():
    """获取支持的导入格式列表"""
    return {"formats": import_service.get_supported_extensions()}
