from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FacetCount, Facets, Game, Pagination, Report, ReportListResponse

# Nombres reales en PostgreSQL
TABLE_REPORTS = "reports"

SORT_COLUMN_MAP = {
    "created_at": "created_at",
    "game.name": "game_name",
    "game.release_year": "release_year",
    "updated_at": "updated_at",
    "progress_percent": """
        CASE report_status
            WHEN 'completed' THEN 100
            WHEN 'processing' THEN 50
            WHEN 'queued' THEN 10
            ELSE 0
        END
    """,
}


class ReportService:
    def __init__(self, db: AsyncSession, user_id: Optional[UUID] = None):
        self.db = db
        self.user_id = user_id

    async def list_reports(
        self,
        genre: Optional[List[str]] = None,
        developer: Optional[List[str]] = None,
        platform: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 12,
    ) -> ReportListResponse:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            items, total = MockDatabaseManager.list_reports(
                genre=genre,
                developer=developer,
                platform=platform,
                status=status,
                year_from=year_from,
                year_to=year_to,
                search=search,
                sort_by=sort_by,
                sort_dir=sort_dir,
                page=page,
                page_size=page_size
            )
            total_pages = (total + page_size - 1) // page_size if total else 0
            pagination = Pagination(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            )
            facets = MockDatabaseManager.get_facets()
            return ReportListResponse(
                items=[self._row_to_report(item) for item in items],
                pagination=pagination,
                facets=facets,
            )

        filters = ["TRUE"]
        params: Dict[str, Any] = {}

        if genre:
            filters.append("(primary_genre = ANY(:genre) OR all_genres && :genre)")
            params["genre"] = genre

        if developer:
            filters.append("developer_name = ANY(:developer)")
            params["developer"] = developer

        if platform:
            filters.append(
                "(primary_platform = ANY(:platform) OR all_platforms && :platform)"
            )
            params["platform"] = platform

        if status:
            filters.append("report_status = ANY(:status)")
            params["status"] = status

        if year_from is not None:
            filters.append("release_year >= :year_from")
            params["year_from"] = year_from

        if year_to is not None:
            filters.append("release_year <= :year_to")
            params["year_to"] = year_to

        if search:
            filters.append(
                """
                to_tsvector(
                    'english',
                    coalesce(game_name, '') || ' ' ||
                    coalesce(markdown_content, '') || ' ' ||
                    coalesce(developer_name, '')
                ) @@ plainto_tsquery('english', :search)
                """
            )
            params["search"] = search

        where_clause = " AND ".join(filters)
        sort_column = SORT_COLUMN_MAP.get(sort_by, "created_at")
        sort_direction = "DESC" if sort_dir.lower() == "desc" else "ASC"

        count_query = text(
            f"SELECT COUNT(*) FROM {TABLE_REPORTS} WHERE {where_clause}"
        )
        count_result = await self.db.execute(count_query, params)
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        list_query = text(
            f"""
            SELECT *
            FROM {TABLE_REPORTS}
            WHERE {where_clause}
            ORDER BY {sort_column} {sort_direction}
            LIMIT :limit OFFSET :offset
            """
        )
        result = await self.db.execute(list_query, params)
        items = result.fetchall()

        total_pages = (total + page_size - 1) // page_size if total else 0
        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        facets = await self._get_facets()

        return ReportListResponse(
            items=[self._row_to_report(item) for item in items],
            pagination=pagination,
            facets=facets,
        )

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            item = MockDatabaseManager.get_report(report_id)
            if not item:
                return None
            return self._row_to_report(item)

        query = text(
            f"""
            SELECT *
            FROM {TABLE_REPORTS}
            WHERE id = :report_id
            """
        )
        result = await self.db.execute(query, {"report_id": str(report_id)})
        item = result.first()
        if not item:
            return None
        return self._row_to_report(item)

    async def get_report_content(
        self, report_id: UUID, format: str
    ) -> Optional[Dict[str, Any]]:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            item = MockDatabaseManager.get_report(report_id)
            if not item:
                return None
            available_formats = {}
            if item.markdown_content or item.url_markdown:
                available_formats["markdown"] = {
                    "content_url": item.url_markdown or "",
                    "download_url": item.url_markdown,
                    "content": item.markdown_content,
                }
            if format not in available_formats:
                return None
            return {"format": format, **available_formats[format]}

        query = text(
            f"""
            SELECT id, game_name, markdown_content, url_markdown, url_json,
                   url_json_rag, url_pdf, json_generated, markdown_generated,
                   json_rag_generated, pdf_generated
            FROM {TABLE_REPORTS}
            WHERE id = :report_id
            """
        )
        result = await self.db.execute(query, {"report_id": str(report_id)})
        item = result.first()
        if not item:
            return None

        available_formats: Dict[str, Dict[str, Any]] = {}

        if item.markdown_content or item.url_markdown:
            available_formats["markdown"] = {
                "content_url": item.url_markdown or "",
                "download_url": item.url_markdown,
                "content": item.markdown_content,
            }

        if item.url_json or item.json_generated:
            available_formats["json"] = {
                "content_url": item.url_json or "",
                "download_url": item.url_json,
            }

        if item.url_json_rag or item.json_rag_generated:
            available_formats["json_rag"] = {
                "content_url": item.url_json_rag or "",
                "download_url": item.url_json_rag,
            }

        if format not in available_formats:
            return None

        return {"format": format, **available_formats[format]}

    async def get_report_pdf_url(self, report_id: UUID) -> Optional[str]:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            item = MockDatabaseManager.get_report(report_id)
            if not item or not item.url_pdf:
                return None
            return item.url_pdf

        query = text(
            f"""
            SELECT url_pdf, pdf_generated
            FROM {TABLE_REPORTS}
            WHERE id = :report_id
            """
        )
        result = await self.db.execute(query, {"report_id": str(report_id)})
        item = result.first()
        if not item or not item.url_pdf:
            return None
        return item.url_pdf

    async def update_report(
        self,
        report_id: UUID,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Optional[Report]:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            item = MockDatabaseManager.update_report(report_id, tags=tags, notes=notes)
            if not item:
                return None
            return self._row_to_report(item)

        if tags is None and notes is None:
            return await self.get_report(report_id)

        # Use ORM for the update — asyncpg TEXT[] parameters fail in raw text() queries
        # due to indeterminate type inference; ORM handles array columns correctly.
        from app.models.report import Report as ReportORM

        orm_result = await self.db.execute(
            select(ReportORM).where(ReportORM.id == report_id)
        )
        report_orm = orm_result.scalar_one_or_none()
        if not report_orm:
            return None

        if tags is not None:
            report_orm.tags = tags
        if notes is not None:
            meta = dict(report_orm.user_metadata_jsonb or {})
            meta["user_notes"] = notes
            report_orm.user_metadata_jsonb = meta

        await self.db.commit()
        await self.db.refresh(report_orm)
        return self._row_to_report(report_orm)

    async def delete_report(self, report_id: UUID) -> bool:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            return False

        query = text(
            f"""
            DELETE FROM {TABLE_REPORTS}
            WHERE id = :report_id
            RETURNING id
            """
        )
        result = await self.db.execute(query, {"report_id": str(report_id)})
        await self.db.commit()
        return result.first() is not None

    async def get_facets(self) -> Facets:
        from app.db.connection import IS_DATABASE_ONLINE
        if not IS_DATABASE_ONLINE:
            from app.db.mock_data import MockDatabaseManager
            return MockDatabaseManager.get_facets()
        return await self._get_facets()

    def _row_to_report(self, row) -> Report:
        status_value = getattr(row, "report_status", "completed")
        pipeline_progress = getattr(row, "pipeline_progress", None)
        if pipeline_progress is None:
            pipeline_progress = 100 if status_value == "completed" else (
                50 if status_value == "processing" else 10 if status_value == "queued" else 0
            )

        all_genres = list(getattr(row, "all_genres", None) or [])
        all_platforms = list(getattr(row, "all_platforms", None) or [])

        game = Game(
            id=str(row.game_id),
            name=row.game_name,
            slug=getattr(row, "game_slug", None),
            release_year=getattr(row, "release_year", None),
            developer=getattr(row, "developer_name", None),
            primary_genre=getattr(row, "primary_genre", None),
            primary_platform=getattr(row, "primary_platform", None),
            all_genres=all_genres,
            all_platforms=all_platforms,
            cover_url=getattr(row, "cover_url", None),
        )

        updated_at = getattr(row, "updated_at", None) or row.created_at

        exec_summary  = getattr(row, "executive_summary_jsonb",  None) or None
        thematic      = getattr(row, "thematic_analysis_jsonb",  None) or None
        conf_analysis = getattr(row, "confidence_analysis_jsonb", None) or None

        return Report(
            id=str(row.id),
            game=game,
            status=status_value,
            current_phase=getattr(row, "current_phase", None),
            pipeline_progress=pipeline_progress,
            confidence_score=getattr(row, "confidence_score", None),
            tags=list(getattr(row, "tags", None) or []),
            created_at=row.created_at,
            updated_at=updated_at,
            executive_summary=exec_summary,
            thematic_analysis=thematic,
            confidence_analysis=conf_analysis,
        )

    async def _get_facets(self) -> Facets:
        status_query = text(
            f"""
            SELECT report_status AS value, COUNT(*) AS count, report_status AS label
            FROM {TABLE_REPORTS}
            GROUP BY report_status
            ORDER BY count DESC
            """
        )

        genre_query = text(
            f"""
            SELECT g AS value, COUNT(*) AS count, g AS label
            FROM {TABLE_REPORTS}, unnest(all_genres) AS g
            WHERE all_genres IS NOT NULL
            GROUP BY g
            ORDER BY count DESC
            """
        )

        platform_query = text(
            f"""
            SELECT p AS value, COUNT(*) AS count, p AS label
            FROM {TABLE_REPORTS}, unnest(all_platforms) AS p
            WHERE all_platforms IS NOT NULL
            GROUP BY p
            ORDER BY count DESC
            """
        )

        developer_query = text(
            f"""
            SELECT developer_name AS value, COUNT(*) AS count, developer_name AS label
            FROM {TABLE_REPORTS}
            WHERE developer_name IS NOT NULL
            GROUP BY developer_name
            ORDER BY count DESC
            """
        )

        year_query = text(
            f"""
            SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
            FROM {TABLE_REPORTS}
            WHERE release_year IS NOT NULL
            """
        )

        status_result = await self.db.execute(status_query)
        genre_result = await self.db.execute(genre_query)
        platform_result = await self.db.execute(platform_query)
        developer_result = await self.db.execute(developer_query)
        year_result = await self.db.execute(year_query)

        status_facets = [
            FacetCount(value=row.value, count=row.count, label=row.label)
            for row in status_result.fetchall()
        ]
        genre_facets = [
            FacetCount(value=row.value, count=row.count, label=row.label)
            for row in genre_result.fetchall()
        ]
        platform_facets = [
            FacetCount(value=row.value, count=row.count, label=row.label)
            for row in platform_result.fetchall()
        ]
        developer_facets = [
            FacetCount(value=row.value, count=row.count, label=row.label)
            for row in developer_result.fetchall()
        ]

        year_row = year_result.first()
        year_range = {
            "min_year": year_row.min_year if year_row and year_row.min_year else 1970,
            "max_year": year_row.max_year if year_row and year_row.max_year else datetime.now().year,
        }

        return Facets(
            genre=genre_facets,
            developer=developer_facets,
            platform=platform_facets,
            status=status_facets,
            year_range=year_range,
        )
