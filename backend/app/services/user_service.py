from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from .auth_service import hash_password


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_list(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    role: str | None = None,
    keyword: str | None = None,
) -> tuple[list[User], int]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if keyword:
        query = query.filter(User.username.contains(keyword) | User.nickname.contains(keyword))
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(User.id).offset(offset).limit(page_size).all()
    return items, total


def create_user(db: Session, data: UserCreate) -> User:
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise ValueError("用户名已存在")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        nickname=data.nickname,
        role=data.role,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, user_id: int, new_password: str) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if user.role == "admin":
        # Check if there's only one admin left
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise ValueError("不能删除唯一的超级管理员")
    db.delete(user)
    db.commit()
