from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from ..services.auth_service import register_user, authenticate_user, create_access_token
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """用户注册（默认注册为学生）"""
    try:
        user = register_user(db, req)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """用户登录，返回 JWT Token"""
    try:
        user = authenticate_user(db, req)
        token = create_access_token({"user_id": user.id, "role": user.role})
        return TokenResponse(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user
