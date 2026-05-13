import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .limiter import limiter

from .config import settings
from .database import engine, Base
from .models import User, Question, PracticeRecord, Category, Exam, ExamQuestion, ExamAttempt, ExamAnswer  # noqa: F401 - register models
from .routers import auth, users, questions as question_router, import_ as import_router, practice, categories, exams
from .services.auth_service import hash_password, verify_password

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("single-choice-practice")



# CSP Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data:;"
        return response


def init_default_admin():
    """Create or update default admin user. Updates password if config changed."""
    from .database import SessionLocal
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                nickname="超级管理员",
                role="admin",
            )
            db.add(admin)
            db.commit()
            logger.info("默认管理员已创建: %s", settings.DEFAULT_ADMIN_USERNAME)
        else:
            # 管理员已存在，检查密码是否与配置一致
            if not verify_password(settings.DEFAULT_ADMIN_PASSWORD, admin.password_hash):
                old_hash = admin.password_hash
                admin.password_hash = hash_password(settings.DEFAULT_ADMIN_PASSWORD)
                db.commit()
                logger.info("默认管理员密码已更新: %s（旧 hash 已替换）", settings.DEFAULT_ADMIN_USERNAME)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables and default admin on startup."""
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表已创建")
    init_default_admin()
    # Warn if SECRET_KEY is still the default value
    if settings.SECRET_KEY == "change-this-to-a-secure-random-string":
        logger.warning(
            "⚠️  SECRET_KEY 仍为默认值，请立即修改！生产环境中应设置环境变量 SECRET_KEY "
            "为一个随机的安全字符串，例如使用命令生成: openssl rand -hex 32"
        )
    yield


app = FastAPI(
    title="刷单选题系统 API",
    description="前后端分离的刷单选题系统后端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS - configured via env, default to localhost origins for development
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:80,http://127.0.0.1,http://127.0.0.1:80").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(question_router.router)
app.include_router(import_router.router)
app.include_router(practice.router)
app.include_router(categories.router)
app.include_router(exams.router)


@app.get("/api/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "1.0.0"}
