from __future__ import annotations

from flask import Flask

from .health import system_bp
from .news import news_bp
from .places import places_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(system_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(places_bp)
