from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, send_from_directory

system_bp = Blueprint("system", __name__)


@system_bp.get("/api/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@system_bp.get("/media/<path:filename>")
def serve_media(filename: str) -> Any:
    media_root = Path(current_app.config["MEDIA_ROOT"])
    return send_from_directory(media_root, filename)
