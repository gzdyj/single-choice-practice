from sqlalchemy.orm import Session

from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_list(
    db: Session,
    page: int = 1,
    page_size: int = 100,
    keyword: str | None = None,
) -> tuple[list[Category], int]:
    query = db.query(Category)
    if keyword:
        query = query.filter(Category.name.contains(keyword))
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Category.id).offset(offset).limit(page_size).all()
    return items, total


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise ValueError(f"分类名称已存在: {data.name}")
    category = Category(name=data.name, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category_by_id(db, category_id)
    if not category:
        raise ValueError("分类不存在")
    # Check name uniqueness if name is being updated
    if data.name is not None and data.name != category.name:
        existing = db.query(Category).filter(Category.name == data.name).first()
        if existing:
            raise ValueError(f"分类名称已存在: {data.name}")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category_by_id(db, category_id)
    if not category:
        raise ValueError("分类不存在")
    # Check if any questions are using this category
    from ..models.question import Question
    question_count = db.query(Question).filter(Question.category_id == category_id).count()
    if question_count > 0:
        raise ValueError(f"该分类下还有 {question_count} 道题目，无法删除。请先移除题目关联。")
    db.delete(category)
    db.commit()


def get_all_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.id).all()
