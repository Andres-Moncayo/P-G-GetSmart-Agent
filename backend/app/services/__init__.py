from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.sql import expression
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models import Report, Game, Pagination, Facets, ReportListResponse, FacetCount

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
        # Use the optimized view for reports
        query = text("""
            SELECT * FROM v_reportes_principal 
            WHERE 1=1
        """)
        
        # Apply filters
        filters = []
        params = {"user_id": str(self.user_id)}
        
        if genre:
            filters.append("primary_genre = ANY(:genre) OR all_genres && :genre")
            params["genre"] = genre
            
        if developer:
            filters.append("developer_name = ANY(:developer)")
            params["developer"] = developer
            
        if platform:
            filters.append("primary_platform = ANY(:platform) OR all_platforms && :platform")
            params["platform"] = platform
            
        if status:
            filters.append("report_status = ANY(:status)")
            params["status"] = status
            
        if year_from:
            filters.append("release_year >= :year_from")
            params["year_from"] = year_from
            
        if year_to:
            filters.append("release_year <= :year_to")
            params["year_to"] = year_to
            
        if search:
            filters.append("to_tsvector('english', game_name || ' ' || COALESCE(markdown_content, '') || ' ' || COALESCE(developer_name, '')) @@ plainto_tsquery('english', :search)")
            params["search"] = search
            
        if filters:
            query = text(f"SELECT * FROM v_reportes_principal WHERE {' AND '.join(filters)}")
        
        # Count total
        count_query = text(f"SELECT COUNT(*) FROM ({str(query).replace('*', 'id')}) as subq").params(**params)
        
        # Apply sorting
        if sort_by in ["created_at", "game_name", "release_year", "updated_at", "confidence_score", "completed_at"]:
            query = text(f"{str(query)} ORDER BY {sort_by} {sort_dir.upper()}")
        else:
            query = text(f"{str(query)} ORDER BY created_at DESC")
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = text(f"{str(query)} LIMIT :page_size OFFSET :offset")
        params["page_size"] = page_size
        params["offset"] = offset
        
        # Execute queries
        result = await self.db.execute(query, params)
        items = result.fetchall()
        
        count_result = await self.db.execute(count_query, params)
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
            items=[await self._row_to_report(item) for item in items],
            pagination=pagination,
            facets=facets
        )

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """
        Get single report by ID
        GET /api/v1/reports/{report_id}
        """
        query = text("""
            SELECT * FROM reportes 
            WHERE id = :report_id 
        """).params(report_id=str(report_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        if not item:
            return None
        
        # Check if user has access (RLS will handle this automatically)
        verify_query = text("SELECT 1 FROM reportes WHERE id = :report_id").params(report_id=str(report_id))
        verify_result = await self.db.execute(verify_query)
        
        if not verify_result.first():
            return None
            
        return await self._row_to_report(item)

    async def get_report_content(self, report_id: UUID, format: str) -> Optional[Dict[str, Any]]:
        """
        Get report content in specified format
        GET /api/v1/reports/{report_id}/content
        """
        query = text("""
            SELECT id, game_name, markdown_content, url_markdown, url_json, url_json_rag, url_pdf,
                   json_generated, markdown_generated, json_rag_generated, pdf_generated
            FROM reportes
            WHERE id = :report_id
        """).params(report_id=str(report_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        if not item:
            return None
        
        # Check if format is available
        available_formats = {}
        if item.markdown_generated and item.url_markdown:
            available_formats["markdown"] = {
                "content_url": item.url_markdown,
                "download_url": item.url_markdown,
                "content": item.markdown_content  # Include actual content
            }
        if item.json_generated and item.url_json:
            available_formats["json"] = {
                "content_url": item.url_json,
                "download_url": item.url_json
            }
        if item.json_rag_generated and item.url_json_rag:
            available_formats["json_rag"] = {
                "content_url": item.url_json_rag,
                "download_url": item.url_json_rag
            }
        
        if format not in available_formats:
            return None
        
        return {
            "format": format,
            **available_formats[format]
        }

    async def get_report_pdf_url(self, report_id: UUID) -> Optional[str]:
        """
        Get PDF download URL
        GET /api/v1/reports/{report_id}/download
        """
        query = text("""
            SELECT url_pdf, pdf_generated
            FROM reportes
            WHERE id = :report_id AND pdf_generated = TRUE
        """).params(report_id=str(report_id))
        
        result = await self.db.execute(query)
        item = result.first()
        
        return item.url_pdf if item and item.pdf_generated and item.url_pdf else None

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
            # Store notes in user_metadata_jsonb
            update_fields["user_metadata_jsonb"] = text("""
                COALESCE(user_metadata_jsonb, '{}') || jsonb_build_object('user_notes', :notes)
            """)
        
        if not update_fields:
            return await self.get_report(report_id)
        
        # Execute update with RLS constraints  
        values_str = []
        params = {"report_id": str(report_id)}
        
        if tags is not None:
            values_str.append("tags = :tags")
            params["tags"] = tags
        if notes is not None:
            values_str.append("user_metadata_jsonb = COALESCE(user_metadata_jsonb, '{}') || jsonb_build_object('user_notes', :notes)")
            params["notes"] = notes
        
        query = text(f"""
            UPDATE reportes 
            SET {', '.join(values_str)}, updated_at = NOW()
            WHERE id = :report_id
            RETURNING *
        """).params(**params)
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        item = result.first()
        if item:
            return await self._row_to_report(item)
        return None

    async def delete_report(self, report_id: UUID) -> bool:
        """
        Delete report and all associated files
        DELETE /api/v1/reports/{report_id}
        """
        query = text("""
            DELETE FROM reportes
            WHERE id = :report_id
            RETURNING id
        """).params(report_id=str(report_id))
        
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

    async def _row_to_report(self, row) -> Report:
        """Convert database row to Report model"""
        # Create Game object
        game = Game(
            id=str(row.game_id),
            name=row.game_name,
            slug=row.game_slug,
            release_year=row.release_year,
            developer=row.developer_name,
            genres=row.all_genres if row.all_genres else [],
            platforms=row.all_platforms if row.all_platforms else []
        )
        
        # Create Report object
        return Report(
            id=row.id,
            game=game,
            status=row.report_status if hasattr(row, 'report_status') else 'completed',
            current_phase=None,  # Not used in new schema
            progress_percent=100 if (hasattr(row, 'report_status') and row.report_status == 'completed') else 0,
            outputs={},  # URLs will be populated as needed
            metadata={},  # Additional metadata from JSONB columns
            summary=None,  # Could extract from executive_summary_jsonb
            tags=row.tags if row.tags else [],
            created_at=row.created_at,
            updated_at=row.updated_at
        )

    async def _get_facets(self) -> Facets:
        """Get facet counts for filtering"""
        
        # Status facets
        status_query = text("""
            SELECT report_status as value, COUNT(*) as count, report_status as label
            FROM reportes 
            GROUP BY report_status
            ORDER BY count DESC
        """)
        
        # Genre facets  
        genre_query = text("""
            SELECT unnest(all_genres) as value, COUNT(*) as count, unnest(all_genres) as label
            FROM reportes 
            WHERE all_genres IS NOT NULL
            GROUP BY unnest(all_genres)
            ORDER BY count DESC
        """)
        
        # Platform facets
        platform_query = text("""
            SELECT unnest(all_platforms) as value, COUNT(*) as count, unnest(all_platforms) as label
            FROM reportes 
            WHERE all_platforms IS NOT NULL
            GROUP BY unnest(all_platforms)
            ORDER BY count DESC
        """)
        
        # Developer facets
        developer_query = text("""
            SELECT developer_name as value, COUNT(*) as count, developer_name as label
            FROM reportes 
            WHERE developer_name IS NOT NULL
            GROUP BY developer_name
            ORDER BY count DESC
        """)
        
        # Year range
        year_query = text("""
            SELECT 
                MIN(release_year) as min_year,
                MAX(release_year) as max_year
            FROM reportes 
            WHERE release_year IS NOT NULL
        """)
        
        # Execute queries
        status_result = await self.db.execute(status_query)
        genre_result = await self.db.execute(genre_query) 
        platform_result = await self.db.execute(platform_query)
        developer_result = await self.db.execute(developer_query)
        year_result = await self.db.execute(year_query)
        
        # Convert to FacetCount objects
        status_facets = [FacetCount(value=row.value, count=row.count, label=row.label) for row in status_result.fetchall()]
        genre_facets = [FacetCount(value=row.value, count=row.count, label=row.label) for row in genre_result.fetchall()]
        platform_facets = [FacetCount(value=row.value, count=row.count, label=row.label) for row in platform_result.fetchall()]
        developer_facets = [FacetCount(value=row.value, count=row.count, label=row.label) for row in developer_result.fetchall()]
        
        # Year range
        year_row = year_result.first()
        year_range = {
            "min_year": year_row.min_year if year_row and year_row.min_year else 1970,
            "max_year": year_row.max_year if year_row and year_row.max_year else datetime.now().year
        }
        
        return Facets(
            genre=genre_facets,
            developer=developer_facets, 
            platform=platform_facets,
            status=status_facets,
            year_range=year_range
        )