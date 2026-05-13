from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse,
)
from ..services import category_service
from ..middleware.auth_middleware import require_role, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/categories", tags=["分类管理"])


@router.get("", response_model=CategoryListResponse)
def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取分类列表（分页，可选关键词搜索）"""
    items, total = category_service.get_category_list(db, page, page_size, keyword)
    return CategoryListResponse(total=total, items=items)


@router.get("/all", response_model=list[CategoryResponse])
def list_all_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取所有分类（不分页，供前端下拉选择）"""
    return category_service.get_all_categories(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """创建分类（管理员）"""
    try:
        return category_service.create_category(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取分类详情"""
    category = category_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """更新分类（管理员）"""
    try:
        return category_service.update_category(db, category_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    """删除分类（管理员，需先移除题目关联）"""
    try:
        category_service.delete_category(db, category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
