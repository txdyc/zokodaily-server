from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, request

from ..db import get_engine
from ..repositories.news import NewsRepository
from ..serializers import serialize_news_detail, serialize_news_summary
from ..utils import build_pagination, parse_int, parse_news_category

news_bp = Blueprint("news", __name__)


@news_bp.get("/api/news")
@news_bp.get("/api/news/search")
def list_news() -> Any:
    repository = NewsRepository(get_engine())
    page = parse_int(request.args.get("page"), 1, minimum=1, maximum=100000)
    page_size = parse_int(request.args.get("page_size"), 10, minimum=1, maximum=50)
    category = parse_news_category(request.args.get("category"))

    rows, total = repository.get_news_list(
        page=page,
        page_size=page_size,
        q=(request.args.get("q") or "").strip(),
        news_date=(request.args.get("date") or "").strip(),
        date_from=(request.args.get("date_from") or "").strip(),
        date_to=(request.args.get("date_to") or "").strip(),
        category=category,
    )
    return jsonify(
        {
            "items": [serialize_news_summary(row) for row in rows],
            "pagination": build_pagination(page, page_size, total),
        }
    )


@news_bp.get("/api/news/<int:news_id>")
def news_detail(news_id: int) -> Any:
    repository = NewsRepository(get_engine())
    row = repository.get_news_detail(news_id)
    if not row:
        abort(404, description="News not found")
    return jsonify(serialize_news_detail(row))
