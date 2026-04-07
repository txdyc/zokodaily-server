from __future__ import annotations

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        error_code = error.code or 500
        error_name = error.name.lower().replace(" ", "_")
        return jsonify({"error": error_name, "message": error.description}), error_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled exception", exc_info=error)
        return jsonify(
            {
                "error": "internal_server_error",
                "message": "An unexpected error occurred.",
            }
        ), 500
