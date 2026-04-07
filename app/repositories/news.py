from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


class NewsRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_news_list(
        self,
        *,
        page: int,
        page_size: int,
        q: str,
        news_date: str,
        date_from: str,
        date_to: str,
        category: int | None,
    ) -> tuple[list[dict[str, Any]], int]:
        filters = ["deleted = b'0'"]
        params: dict[str, Any] = {
            "limit": page_size,
            "offset": (page - 1) * page_size,
        }

        if q:
            filters.append(
                "("
                "title LIKE :q OR chinese_title LIKE :q OR summary LIKE :q OR chinese_summary LIKE :q OR "
                "content LIKE :q OR chinese_content LIKE :q OR bilingual_content LIKE :q"
                ")"
            )
            params["q"] = f"%{q.strip()}%"
        if news_date:
            filters.append("news_date = :news_date")
            params["news_date"] = news_date
        if date_from:
            filters.append("news_date >= :date_from")
            params["date_from"] = date_from
        if date_to:
            filters.append("news_date <= :date_to")
            params["date_to"] = date_to
        if category is not None:
            filters.append("category = :category")
            params["category"] = category

        where_clause = " AND ".join(filters)
        count_sql = text(f"SELECT COUNT(*) FROM zokodaily_news WHERE {where_clause}")
        list_sql = text(
            f"""
            SELECT
              n.id,
              n.site,
              n.title,
              n.chinese_title,
              n.news_date,
              n.category,
              (
                SELECT i.local_path
                FROM zokodaily_news_image i
                WHERE i.news_id = n.id AND i.deleted = b'0'
                ORDER BY i.is_cover DESC, i.sort_order ASC, i.id ASC
                LIMIT 1
              ) AS thumbnail_path
            FROM zokodaily_news n
            WHERE {where_clause}
            ORDER BY n.news_date DESC, n.id DESC
            LIMIT :limit OFFSET :offset
            """
        )
        with self.engine.begin() as conn:
            total = int(conn.execute(count_sql, params).scalar_one())
            rows = [dict(row._mapping) for row in conn.execute(list_sql, params)]
        return rows, total

    def get_news_detail(self, news_id: int) -> dict[str, Any] | None:
        news_sql = text(
            """
            SELECT
              id,
              site,
              title,
              chinese_title,
              summary,
              chinese_summary,
              news_date,
              content,
              chinese_content,
              bilingual_content,
              url,
              category,
              creator,
              create_time,
              update_time
            FROM zokodaily_news
            WHERE id = :news_id AND deleted = b'0'
            """
        )
        images_sql = text(
            """
            SELECT
              id,
              source_url,
              local_path,
              img_desc,
              is_cover,
              sort_order
            FROM zokodaily_news_image
            WHERE news_id = :news_id AND deleted = b'0'
            ORDER BY is_cover DESC, sort_order ASC, id ASC
            """
        )
        with self.engine.begin() as conn:
            row = conn.execute(news_sql, {"news_id": news_id}).mappings().first()
            if not row:
                return None
            images = [dict(image) for image in conn.execute(images_sql, {"news_id": news_id}).mappings()]
        payload = dict(row)
        payload["images"] = images
        return payload
