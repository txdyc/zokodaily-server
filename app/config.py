from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy.engine import URL


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _as_csv(value: str | None) -> list[str] | str:
    if not value or value.strip() == "*":
        return "*"
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or "*"


def _resolve_path(value: str, base_dir: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    return (base_dir / candidate).resolve()


class BaseConfig:
    def __init__(self) -> None:
        server_root = Path(__file__).resolve().parents[1]
        workspace_root = server_root.parent

        self.ENV_NAME = os.getenv("APP_ENV", "development").lower()
        self.SERVER_ROOT = server_root
        self.WORKSPACE_ROOT = workspace_root

        self.JSON_AS_ASCII = False
        self.JSON_SORT_KEYS = False
        self.DEBUG = False
        self.TESTING = False

        self.FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
        self.FLASK_PORT = _as_int(os.getenv("FLASK_PORT"), 5000)

        self.DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")
        self.DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
        self.DB_PORT = _as_int(os.getenv("DB_PORT"), 3306)
        self.DB_NAME = os.getenv("DB_NAME", "zokodaily")
        self.DB_USER = os.getenv("DB_USER", "root")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        self.DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
        self.DB_USE_UNICODE = _as_bool(os.getenv("DB_USE_UNICODE"), True)
        self.DATABASE_URL = self._build_database_url()

        self.MEDIA_ROOT = _resolve_path(
            os.getenv("MEDIA_ROOT", "../spider/downloads"),
            server_root,
        )
        self.CORS_ORIGINS = _as_csv(os.getenv("CORS_ORIGINS", "*"))

    def _build_database_url(self) -> str:
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            return explicit_url
        return URL.create(
            self.DB_DRIVER,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": self.DB_CHARSET},
        ).render_as_string(hide_password=False)


class DevelopmentConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), True)


class ProductionConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), False)


CONFIG_MAPPING = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config(name: str) -> BaseConfig:
    config_class = CONFIG_MAPPING.get(name.lower(), DevelopmentConfig)
    return config_class()
