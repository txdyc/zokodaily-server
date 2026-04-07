from __future__ import annotations

import json
import math
import re
from typing import Any

NEWS_CATEGORY_LABELS = {
    0: "general",
    1: "political",
    2: "economy",
    3: "entertaining",
    4: "headline",
}
NEWS_CATEGORY_LOOKUP = {str(key): key for key in NEWS_CATEGORY_LABELS}
NEWS_CATEGORY_LOOKUP.update({value: key for key, value in NEWS_CATEGORY_LABELS.items()})


def parse_int(value: str | None, default: int, *, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def parse_news_category(value: str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    normalized = str(value).strip().lower()
    return NEWS_CATEGORY_LOOKUP.get(normalized)


def parse_closing_time(opening_text: str) -> str:
    if not opening_text:
        return ""
    patterns = [
        r"Closes?\s+([0-9:\sAPMapm\.]+)",
        r"Opens?\s+until\s+([0-9:\sAPMapm\.]+)",
        r"结束营业时间[:：]?\s*([0-9:\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, opening_text, flags=re.I)
        if match:
            return match.group(1).strip()
    return ""


def bit_to_bool(value: Any) -> bool:
    if isinstance(value, (bytes, bytearray)):
        return any(value)
    return bool(value)


def json_loads_safe(value: str | None) -> list[Any]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def isoformat_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def build_pagination(page: int, page_size: int, total: int) -> dict[str, int]:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }
