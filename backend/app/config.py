"""Application configuration."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", os.getenv("NODE_ENV", "development"))
    DEBUG = FLASK_ENV == "development"
    TESTING = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"
    )

    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "zenith-intelligence-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    MULTIMODAL_API_KEY = os.getenv("MULTIMODAL_API_KEY", "")
    MULTIMODAL_API_URL = os.getenv(
        "MULTIMODAL_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    )
    MULTIMODAL_MODEL = os.getenv("MULTIMODAL_MODEL", "glm-4.6v-flashx")

    ARK_API_KEY = os.getenv("ARK_API_KEY", "")
    ARK_BASE_URL = os.getenv(
        "ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
    )
    ARK_VISION_MODEL = os.getenv(
        "ARK_VISION_MODEL", "doubao-seed-2-0-pro-260215"
    )

    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_API_URL = os.getenv(
        "MINIMAX_API_URL", "https://api.minimaxi.com/v1/chat/completions"
    )
    MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")

    CHATGLM_API_KEY = os.getenv("CHATGLM_API_KEY", "")
    CHATGLM_API_URL = os.getenv(
        "CHATGLM_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    )
    CHATGLM_MODEL = os.getenv("CHATGLM_MODEL", "glm-4.7-flashx")
    CHATGLM_ENABLE_THINKING = _to_bool(os.getenv("CHATGLM_ENABLE_THINKING"), False)

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "minimax")

    REQUEST_TIMEOUT = _to_int(os.getenv("REQUEST_TIMEOUT"), 120)
    MAX_IMAGE_SIZE = _to_int(os.getenv("MAX_IMAGE_SIZE"), 5 * 1024 * 1024)

    RATE_LIMIT_WINDOW_MS = _to_int(os.getenv("RATE_LIMIT_WINDOW_MS"), 60000)
    RATE_LIMIT_MAX_REQUESTS = _to_int(os.getenv("RATE_LIMIT_MAX_REQUESTS"), 30)
    RATE_LIMIT_WINDOW_SECONDS = max(1, RATE_LIMIT_WINDOW_MS // 1000)

    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
