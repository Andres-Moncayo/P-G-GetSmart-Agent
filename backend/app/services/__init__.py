from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.sql import expression
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models import Report, Game, Pagination, Facets, ReportListResponse
from app.db.connection import AsyncSession

class ReportService:
    
    def __init__(self, db: AsyncSession, user_id: UUID):
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
        page_size: int = 12
    ) -> ReportListResponse:
        """
        List reports with filtering, sorting and pagination
        GET /api/v1/reports
        """
        query = select(self._get_report_summary_query())
        
        # Apply filters
        filters = [text("owner_id = :user_id")]
        params = {"user_id": str(self.user_id)}
        
        if genre:
            filters.append(text("game_genres = ANY(:genre)"))
            params["genre"] = genre
            
        if developer:
            filters.append(text("developer = ANY(:developer)"))
            params["developer"] = developer
            
        if platform:
            filters.append(text("game_platforms = ANY(:platform)"))
            params["platform"] = platform
            
        if status:
            filters.append(text("status = ANY(:status)"))
            params["status"] = status
            
        if year_from:
            filters.append(text("release_year >= :year_from"))
            params["year_from"] = year_from
            
        if year_to:
            filters.append(text("release_year <= :year_to"))
            params["year_to"] = year_to
            
        if search:
            filters.append(text("search_vector @@ plainto_tsquery('english', :search)"))
            params["search"] = search
            
        if len(filters) > 1:
            query = query.where(and_(*filters))
        
        # Count total
        count_query = select(func.count()).select_from(
            select(self._get_report_summary_query())
            .where(and_(*filters) if len(filters) > 1 else filters[0])
            .subquery()
        )
        
        # Apply sorting
        if sort_by == "game.name":
            query = query.order_by(
                text(f"game_name {sort_dir}")
            )
        else:
            query = query.order_by(text(f"{sort_by} {sort_dir}"))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute queries
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Create pagination info
        total_pages = (total + page_size - 1) // page_size
        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        # Get facets
        facets = await self._get_facets()
        
        return ReportListResponse(
            items=[await self._dict_to_report(item) for item in items],
            pagination=pagination,
            facets=facets
        )

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """
        Get single report by ID
        GET /api/v1/reports/{report_id}
        """
        query = select(self._get_report_detail_query()).where(
            and_(
                text("id = :report_id"),
                text("owner_id = :user_id")
            )
        ).params(report_id=str(report_id), user_id=str(self.user_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        if not item:
            return None
            
        return await self._dict_to_report(item[0])

    async def get_report_content(self, report_id: UUID, format: str) -> Optional[Dict[str, Any]]:
        """
        Get report content in specified format
        GET /api/v1/reports/{report_id}/content
        """
        query = text("""
            SELECT id, game_name, markdown_url, json_url, json_rag_url
            FROM report_details
            WHERE id = :report_id AND owner_id = :user_id
        """).params(report_id=str(report_id), user_id=str(self.user_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        if not item:
            return None
        
        # Return appropriate content based on format
        content_map = {
            "markdown": item.markdown_url,
            "json": item.json_url,
            "json_rag": item.json_rag_url
        }
        
        return {
            "format": format,
            "content_url": content_map.get(format),
            "download_url": content_map.get(format)
        }

    async def get_report_pdf_url(self, report_id: UUID) -> Optional[str]:
        """
        Get PDF download URL
        GET /api/v1/reports/{report_id}/download
        """
        query = text("""
            SELECT pdf_url
            FROM reports
            WHERE id = :report_id AND owner_id = :user_id
        """).params(report_id=str(report_id), user_id=str(self.user_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        return item.pdf_url if item else None

    async def update_report(self, report_id: UUID, tags: Optional[List[str]] = None, notes: Optional[str] = None) -> Optional[Report]:
        """
        Update report metadata (tags, notes only)
        PATCH /api/v1/reports/{report_id}
        """
        # Build update dict with only allowed fields
        update_fields = {}
        if tags is not None:
            update_fields["tags"] = tags
        if notes is not None:
            update_fields["notes"] = notes
        
        if not update_fields:
            return await self.get_report(report_id)
        
        # Execute update with RLS constraints
        values_str = ", ".join([f"{k} = :{k}" for k in update_fields.keys()])
        params = {**update_fields, "report_id": str(report_id), "user_id": str(self.user_id)}
        
        query = text(f"""
            UPDATE reports 
            SET {values_str}, updated_at = NOW()
            WHERE id = :report_id AND owner_id = :user_id
            RETURNING *
        """).params(**params)
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        item = result.first()
        if item:
            return await self.get_report(report_id)
        return None

    async def delete_report(self, report_id: UUID) -> bool:
        """
        Delete report and all associated files
        DELETE /api/v1/reports/{report_id}
        """
        query = text("""
            DELETE FROM reports
            WHERE id = :report_id AND owner_id = :user_id
            RETURNING id
        """).params(report_id=str(report_id), user_id=str(self.user_id))
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.first() is not None

    async def get_facets(self) -> Facets:
        """
        Get available filter options with counts
        GET /api/v1/reports/facets
        """
        return await self._get_facets()

    # ============================================================
    # Helper Methods
    # ============================================================

    def _get_report_summary_query(self):
        """Base query for report summaries"""
        return text("""
            SELECT 
                r.id, r.status, r.progress_percent, r.created_at, r.updated_at, r.tags,
                g.id as game_id, g.name as game_name, g.slug as game_slug,
                g.release_year, g.developer, g.cover_url,
                ARRAY_AGG(DISTINCT gen.name) as game_genres,
                ARRAY_AGG(DISTINCT plat.name) as game_platforms
            FROM reports r
            JOIN games g ON r.game_id = g.id
            LEFT JOIN game_genres gg ON g.id = gg.game_id
            LEFT JOIN genres gen ON gg.genre_id = gen.id
            LEFT JOIN game_platforms gp ON g.id = gp.game_id
            LEFT JOIN platforms plat ON gp.platform_id = plat.id
            WHERE {where_clause}
            GROUP BY r.id, g.id
        """)

    def _get_report_detail_query(self):
        """Base query for detailed report info"""
        return text("""
            SELECT 
                r.*, g.*, 
                u.username as owner_username,
                ARRAY_AGG(DISTINCT gen.name) as game_genres,
                ARRAY_AGG(DISTINCT plat.name) as game_platforms
            FROM reports r
            JOIN games g ON r.game_id = g.id
            JOIN users u ON r.owner_id = u.id
            LEFT JOIN game_genres gg ON g.id = gg.game_id
            LEFT JOIN genres gen ON gg.genre_id = gen.id
            LEFT JOIN game_platforms gp ON g.id = gp.game_id
            LEFT JOIN platforms plat ON gp.platform_id = plat.id
            WHERE {where_clause}
        """)

    async def _get_facets(self) -> Facets:
        """Getfacet counts"""
        
        # Status facets
        status_query = text("""
            SELECT status, COUNT(*) as count, status as label
            FROM reports 
            WHERE owner_id = :user_id
            GROUP BY status
        """).params(user_id=str(self.user_id))
        
        # Genre facets
        genre_query = text("""
            SELECT gen.name as value, COUNT(r.id) as count, gen.name as label
            FROM reports r
            JOIN games g ON r.game_id = g.id
            JOIN game_genres gg ON g.id = gg.game_id
            JOIN genres gen ON gg.genre_id = gen.id
            WHERE r.owner_id = :user_id
            GROUP BY gen.name
        """).params(user_id=str(self.user_id))
        
        # Developer facets
        developer_query = text("""
            SELECT g.developer as value, COUNT(r.id) as count, g.developer as label
            FROM reports r
            JOIN games g ON r.game_id = g.id
            WHERE r.owner_id = :user_id AND g.developer IS NOT NULL
            GROUP BY g.developer
        """).params(user_id=str(self.user_id))
        
        # Platform facets
        platform_query = text("""
            SELECT plat.name as value, COUNT(DISTINCT r.id) as count, plat.name as label
            FROM reports r
            JOIN games g ON r.game_id = g.id
            JOIN game_platforms gp ON g.id = gp.game_id
            JOIN platforms plat ON gp.platform_id = plat.id
            WHERE r.owner_id = :user_id
            GROUP BY plat.name
        """).params(user_id=str(self.user_id))
        
        # Year range
        year_query = text("""
            SELECT 
                MIN(g.release_year) as min_year,
                MAX(g.release_year) as max_year
            FROM reports r
            JOIN games g ON r.game_id = g.id
            WHERE r.owner_id = :user_id AND g.release_year IS NOT NULL
        """).params(user_id=str(self.user_id))
        
        # Execute all queries
        status_result = await self.db.execute(status_query)
        genre_result = await self.db.execute(genre_query)
        developer_result = await self.db.execute(developer_query)
        platform_result = await self.db.execute(platform_query)
        year_result = await self.db.execute(year_query)
        
        # Build facets
        facets = Facets()
        facets.genre = [FacetCount(value=row.value, count=row.count, label=row.label) for row in genre_result.fetchall()]
        facets.developer = [FacetCount(value=row.value, count=row.count, label=row.label) for row in developer_result.fetchall()]
        facets.platform = [FacetCount(value=row.value, count=row.count, label=row.label) for row in platform_result.fetchall()]
        facets.status = [FacetCount(value=row.status, count=row.count, label=row.label) for row in status_result.fetchall()]
        
        year_data = year_result.first()
        if year_data:
            facets.year_range = {"min": year_data.min_year or 1980, "max": year_data.max_year or 2030}
        else:
            facets.year_range = {"min": 1980, "max": 2030}
            
        return facets

    async def _dict_to_report(self, data: Any) -> Report:
        """Convert database result to Report model"""
        game = Game(
            id=data.game_id if hasattr(data, 'game_id') else data.id,
            name=data.game_name if hasattr(data, 'game_name') else data.name,
            slug=data.slug,
            release_year=data.release_year,
            developer=data.developer,
            genres=getattr(data, 'game_genres', []),
            platforms=getattr(data, 'game_platforms', []),
            cover_url=getattr(data, 'cover_url', None)
        )
        
        return Report(
            id=data.id,
            game=game,
            status=data.status,
            current_phase=getattr(data, 'current_phase', None),
            progress_percent=getattr(data, 'progress_percent', 0),
            outputs={},
            metadata={},
            summary=None,
            tags=getattr(data, 'tags', []),
            created_at=data.created_at,
            updated_at=data.updated_at
        )