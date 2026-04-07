from __future__ import annotations

from typing import Any

from flask import url_for

from .utils import (
    NEWS_CATEGORY_LABELS,
    bit_to_bool,
    isoformat_or_none,
    json_loads_safe,
    parse_closing_time,
)


def media_url(local_path: str | None) -> str | None:
    if not local_path:
        return None
    normalized = local_path.replace("\\", "/").lstrip("/")
    prefix = "downloads/"
    relative = normalized[len(prefix) :] if normalized.startswith(prefix) else normalized
    return url_for("system.serve_media", filename=relative, _external=False)


def serialize_news_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "site": row["site"],
        "title": row["title"],
        "chinese_title": row.get("chinese_title") or "",
        "news_date": isoformat_or_none(row.get("news_date")),
        "category": row["category"],
        "category_label": NEWS_CATEGORY_LABELS.get(row["category"], "unknown"),
        "thumbnail_path": row.get("thumbnail_path") or "",
        "thumbnail_url": media_url(row.get("thumbnail_path")),
    }


def serialize_news_detail(row: dict[str, Any]) -> dict[str, Any]:
    images = [
        {
            "id": image["id"],
            "source_url": image.get("source_url") or "",
            "local_path": image.get("local_path") or "",
            "image_url": media_url(image.get("local_path")),
            "description": image.get("img_desc") or "",
            "is_cover": bit_to_bool(image.get("is_cover")),
            "sort_order": image.get("sort_order"),
        }
        for image in row.get("images", [])
    ]
    cover_image = images[0] if images else None
    return {
        "id": row["id"],
        "site": row["site"],
        "source_url": row.get("url"),
        "news_date": isoformat_or_none(row.get("news_date")),
        "category": row["category"],
        "category_label": NEWS_CATEGORY_LABELS.get(row["category"], "unknown"),
        "creator": row.get("creator") or "",
        "title": row["title"],
        "chinese_title": row.get("chinese_title") or "",
        "summary": row.get("summary") or "",
        "chinese_summary": row.get("chinese_summary") or "",
        "content": row.get("content") or "",
        "chinese_content": row.get("chinese_content") or "",
        "bilingual_content": row.get("bilingual_content") or "",
        "cover_image": cover_image,
        "images": images,
        "create_time": isoformat_or_none(row.get("create_time")),
        "update_time": isoformat_or_none(row.get("update_time")),
    }


def serialize_place_category(row: dict[str, Any]) -> dict[str, Any]:
    keyword = row["search_keyword"]
    return {
        "search_keyword": keyword,
        "display_name": keyword.replace("_", " ").title(),
        "place_count": int(row.get("place_count") or 0),
        "sample_category": row.get("sample_category") or "",
    }


def serialize_place_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "place_hash": row["place_hash"],
        "record_hash": row["record_hash"],
        "name": row["name"],
        "category": row.get("category") or "",
        "search_keyword": row.get("search_keyword") or "",
        "opening_text": row.get("opening_text") or "",
        "closing_time": parse_closing_time(row.get("opening_text") or ""),
        "cover_image_path": row.get("cover_image_path") or "",
        "cover_image_url": media_url(row.get("cover_image_path")),
        "rating": row.get("rating") or "",
        "review_count": row.get("review_count") or "",
    }


def serialize_place_detail(row: dict[str, Any]) -> dict[str, Any]:
    images = []
    for image in row.get("images", []):
        images.append(
            {
                "image_hash": image["image_hash"],
                "record_hash": image["record_hash"],
                "place_hash": image["place_hash"],
                "detail_url": image.get("detail_url") or "",
                "source_url": image.get("image_url") or "",
                "local_path": image.get("local_path") or "",
                "image_url": media_url(image.get("local_path")),
                "image_order": image.get("image_order"),
                "downloaded_at": isoformat_or_none(image.get("downloaded_at")),
            }
        )

    image_paths = json_loads_safe(row.get("image_paths_json"))
    return {
        "place_hash": row["place_hash"],
        "record_hash": row["record_hash"],
        "search_keyword": row.get("search_keyword") or "",
        "search_rank": row.get("search_rank") or "",
        "name": row.get("name") or "",
        "category": row.get("category") or "",
        "address": row.get("address") or "",
        "phone": row.get("phone") or "",
        "website": row.get("website") or "",
        "rating": row.get("rating") or "",
        "review_count": row.get("review_count") or "",
        "opening_text": row.get("opening_text") or "",
        "closing_time": parse_closing_time(row.get("opening_text") or ""),
        "plus_code": row.get("plus_code") or "",
        "latitude": row.get("latitude") or "",
        "longitude": row.get("longitude") or "",
        "detail_url": row.get("detail_url") or "",
        "source_search_url": row.get("source_search_url") or "",
        "raw_text": row.get("raw_text") or "",
        "cover_image_path": row.get("cover_image_path") or "",
        "cover_image_url": media_url(row.get("cover_image_path")),
        "image_paths": image_paths,
        "image_urls": [media_url(path) for path in image_paths if path],
        "image_count": row.get("image_count") or "0",
        "crawled_at": isoformat_or_none(row.get("crawled_at")),
        "images": images,
    }
