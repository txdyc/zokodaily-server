from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


class PlacesRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_place_categories(self) -> list[dict[str, Any]]:
        sql = text(
            """
            SELECT
              search_keyword,
              COUNT(DISTINCT place_hash) AS place_count,
              MIN(category) AS sample_category
            FROM google_maps_places
            GROUP BY search_keyword
            ORDER BY search_keyword ASC
            """
        )
        with self.engine.begin() as conn:
            return [dict(row._mapping) for row in conn.execute(sql)]

    def get_places(
        self,
        *,
        page: int,
        page_size: int,
        q: str,
        search_keyword: str,
        category: str,
    ) -> tuple[list[dict[str, Any]], int]:
        filters = ["rn = 1"]
        params: dict[str, Any] = {
            "limit": page_size,
            "offset": (page - 1) * page_size,
        }
        if q:
            filters.append("(name LIKE :q OR category LIKE :q OR address LIKE :q OR raw_text LIKE :q)")
            params["q"] = f"%{q.strip()}%"
        if search_keyword:
            filters.append("search_keyword = :search_keyword")
            params["search_keyword"] = search_keyword
        if category:
            filters.append("category LIKE :category")
            params["category"] = f"%{category.strip()}%"

        where_clause = " AND ".join(filters)
        cte = """
            WITH ranked_places AS (
              SELECT
                p.*,
                ROW_NUMBER() OVER (
                  PARTITION BY p.place_hash
                  ORDER BY
                    CASE
                      WHEN p.search_rank REGEXP '^[0-9]+$' THEN CAST(p.search_rank AS UNSIGNED)
                      ELSE 999999
                    END ASC,
                    p.crawled_at DESC,
                    p.record_hash DESC
                ) AS rn
              FROM google_maps_places p
            )
        """
        count_sql = text(
            cte
            + f"""
            SELECT COUNT(*)
            FROM ranked_places
            WHERE {where_clause}
            """
        )
        list_sql = text(
            cte
            + f"""
            SELECT
              place_hash,
              record_hash,
              name,
              category,
              search_keyword,
              opening_text,
              cover_image_path,
              rating,
              review_count
            FROM ranked_places
            WHERE {where_clause}
            ORDER BY name ASC
            LIMIT :limit OFFSET :offset
            """
        )
        with self.engine.begin() as conn:
            total = int(conn.execute(count_sql, params).scalar_one())
            rows = [dict(row._mapping) for row in conn.execute(list_sql, params)]
        return rows, total

    def get_place_detail(self, place_hash: str) -> dict[str, Any] | None:
        detail_sql = text(
            """
            WITH ranked_places AS (
              SELECT
                p.*,
                ROW_NUMBER() OVER (
                  PARTITION BY p.place_hash
                  ORDER BY
                    CASE
                      WHEN p.search_rank REGEXP '^[0-9]+$' THEN CAST(p.search_rank AS UNSIGNED)
                      ELSE 999999
                    END ASC,
                    p.crawled_at DESC,
                    p.record_hash DESC
                ) AS rn
              FROM google_maps_places p
            )
            SELECT *
            FROM ranked_places
            WHERE place_hash = :place_hash AND rn = 1
            """
        )
        images_sql = text(
            """
            SELECT
              image_hash,
              record_hash,
              place_hash,
              detail_url,
              image_url,
              local_path,
              image_order,
              downloaded_at
            FROM google_maps_place_images
            WHERE place_hash = :place_hash
            ORDER BY
              CASE
                WHEN image_order REGEXP '^[0-9]+$' THEN CAST(image_order AS UNSIGNED)
                ELSE 999999
              END ASC,
              image_hash ASC
            """
        )
        with self.engine.begin() as conn:
            row = conn.execute(detail_sql, {"place_hash": place_hash}).mappings().first()
            if not row:
                return None
            images = [dict(image) for image in conn.execute(images_sql, {"place_hash": place_hash}).mappings()]
        payload = dict(row)
        payload["images"] = images
        return payload
