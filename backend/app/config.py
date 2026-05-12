import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'quiz.db'}",
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-to-a-secure-random-string")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "8"))

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Default admin
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")


settings = Settings()
