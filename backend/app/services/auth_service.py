from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User
from ..schemas.user import LoginRequest, RegisterRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def register_user(db: Session, req: RegisterRequest) -> User:
    """Register a new user. Raises ValueError if username already exists."""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise ValueError("用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.username,
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, req: LoginRequest) -> User:
    """Authenticate user. Raises ValueError on failure."""
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise ValueError("用户名或密码错误")
    if not user.is_active:
        raise ValueError("账户已被禁用")
    if not verify_password(req.password, user.password_hash):
        raise ValueError("用户名或密码错误")
    return user
