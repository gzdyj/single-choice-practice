from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordReset,
)
from ..services import user_service
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str = Query(None, regex="^(admin|teacher|student)$"),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    """管理员：获取用户列表（分页）"""
    items, total = user_service.get_user_list(db, page, page_size, role, keyword)
    return UserListResponse(total=total, items=items)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    """管理员：创建用户"""
    try:
        return user_service.create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看用户详情（管理员可查看任意用户，普通用户只能查看自己）"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户信息（管理员可更新任意用户，普通用户只能更新自己）"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限")
    try:
        return user_service.update_user(db, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    """管理员：删除用户"""
    try:
        user_service.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_password(
    user_id: int,
    data: PasswordReset,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    """管理员：重置用户密码"""
    try:
        return user_service.reset_password(db, user_id, data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
