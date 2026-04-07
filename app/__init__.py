from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .api import register_blueprints
from .config import get_config
from .db import init_app as init_db
from .errors import register_error_handlers


def load_environment() -> None:
    server_root = Path(__file__).resolve().parents[1]
    app_env = os.getenv("APP_ENV", "development").lower()
    load_dotenv(server_root / ".env", override=False)
    load_dotenv(server_root / f".env.{app_env}", override=False)


def create_app(config_name: str | None = None) -> Flask:
    load_environment()
    selected_config = config_name or os.getenv("APP_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(get_config(selected_config))

    cors_origins = app.config["CORS_ORIGINS"]
    CORS(
        app,
        resources={
            r"/api/*": {"origins": cors_origins},
            r"/media/*": {"origins": cors_origins},
        },
    )

    init_db(app)
    register_blueprints(app)
    register_error_handlers(app)
    return app
