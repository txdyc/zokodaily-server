from __future__ import annotations

from flask import Flask, current_app
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _build_connect_args(app: Flask) -> dict[str, object]:
    database_url = app.config["DATABASE_URL"]
    if not database_url.startswith("mysql"):
        return {}
    return {
        "use_unicode": app.config["DB_USE_UNICODE"],
        "charset": app.config["DB_CHARSET"],
    }


def init_app(app: Flask) -> None:
    engine = create_engine(
        app.config["DATABASE_URL"],
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args=_build_connect_args(app),
    )
    app.extensions["db_engine"] = engine


def get_engine() -> Engine:
    return current_app.extensions["db_engine"]
