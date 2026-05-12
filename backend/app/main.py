from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .models import User, Question, PracticeRecord  # noqa: F401 - register models
from .routers import auth, users, questions as question_router, import_ as import_router, practice
from .services.auth_service import hash_password


def init_default_admin():
    """Create default admin user if not exists."""
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
            print(f"✓ 默认管理员已创建: {settings.DEFAULT_ADMIN_USERNAME}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables and default admin on startup."""
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表已创建")
    init_default_admin()
    yield


app = FastAPI(
    title="刷单选题系统 API",
    description="前后端分离的刷单选题系统后端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/api/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": "1.0.0"}
