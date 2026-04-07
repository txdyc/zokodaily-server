from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, request

from ..db import get_engine
from ..repositories.places import PlacesRepository
from ..serializers import serialize_place_category, serialize_place_detail, serialize_place_summary
from ..utils import build_pagination, parse_int

places_bp = Blueprint("places", __name__)


@places_bp.get("/api/place-categories")
def place_categories() -> Any:
    repository = PlacesRepository(get_engine())
    rows = repository.get_place_categories()
    return jsonify({"items": [serialize_place_category(row) for row in rows]})


@places_bp.get("/api/places")
def places_list() -> Any:
    repository = PlacesRepository(get_engine())
    page = parse_int(request.args.get("page"), 1, minimum=1, maximum=100000)
    page_size = parse_int(request.args.get("page_size"), 10, minimum=1, maximum=50)

    rows, total = repository.get_places(
        page=page,
        page_size=page_size,
        q=(request.args.get("q") or "").strip(),
        search_keyword=(request.args.get("search_keyword") or "").strip(),
        category=(request.args.get("category") or "").strip(),
    )
    return jsonify(
        {
            "items": [serialize_place_summary(row) for row in rows],
            "pagination": build_pagination(page, page_size, total),
        }
    )


@places_bp.get("/api/places/<string:place_hash>")
def place_detail(place_hash: str) -> Any:
    repository = PlacesRepository(get_engine())
    row = repository.get_place_detail(place_hash)
    if not row:
        abort(404, description="Place not found")
    return jsonify(serialize_place_detail(row))
