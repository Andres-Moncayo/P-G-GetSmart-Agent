"""
Phase 4 Database Integration Tests

Tests for the database storage components added in Phase 4:
- AnalysisReport model and operations
- PipelineStatus tracking 
- ReportService business logic
- API endpoints for report retrieval
"""

import asyncio
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.models.report import AnalysisReport, PipelineStatus, RawAnalysisData
from app.repositories.report_repository import ReportRepository, PipelineStatusRepository, RawDataRepository
from app.services.report_service import ReportService
from app.db.connection import get_async_session


@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    async for session in get_async_session():
        yield session
        break


@pytest.fixture
async def report_repository(test_db_session):
    """Create report repository for testing."""
    return ReportRepository(test_db_session)


@pytest.fixture
async def pipeline_repository(test_db_session):
    """Create pipeline status repository for testing."""
    return PipelineStatusRepository(test_db_session)


@pytest.fixture
async def raw_data_repository(test_db_session):
    """Create raw data repository for testing."""
    return RawDataRepository(test_db_session)


@pytest.fixture
async def report_service():
    """Create report service for testing."""
    return ReportService()


class TestAnalysisReportModel:
    """Test AnalysisReport model and relationships."""
    
    async def test_create_report_model(self, test_db_session):
        """Test creating an AnalysisReport instance."""
        report_data = {
            "game_id": "test-game-123",
            "game_title": "Test Game",
            "platform": "steam",
            "title": "Analysis Report: Test Game",
            "markdown_content": "# Test Report\n\nThis is a test.",
            "json_content": {"test": "data", "metadata": {"version": "1.0"}},
            "summary": "A test report for the game",
            "status": "completed",
            "confidence_score": 0.85,
            "quality_rating": "good",
            "word_count": 5,
            "data_completeness": 0.9,
            "phases_completed": ["phase1", "phase2", "phase3"],
            "total_phases": 4
        }
        
        report = AnalysisReport(**report_data)
        test_db_session.add(report)
        await test_db_session.commit()
        await test_db_session.refresh(report)
        
        assert report.id is not None
        assert report.game_id == "test-game-123"
        assert report.status == "completed"
        assert report.created_at is not None
        assert report.updated_at is not None


class TestPipelineStatusModel:
    """Test PipelineStatus model and relationships."""
    
    async def test_create_pipeline_status(self, test_db_session):
        """Test creating a PipelineStatus instance."""
        # First create a report to link to
        report = AnalysisReport(
            game_id="test-game-456",
            game_title="Test Game 2",
            platform="epic",
            title="Analysis Report: Test Game 2",
            markdown_content="Test content",
            json_content={"data": "test"},
            status="pending"
        )
        test_db_session.add(report)
        await test_db_session.commit()
        
        # Create pipeline status
        status_data = {
            "report_id": report.id,
            "phase_name": "phase1",
            "status": "running",
            "progress_percentage": 50.0,
            "retry_count": 0
        }
        
        status = PipelineStatus(**status_data)
        test_db_session.add(status)
        await test_db_session.commit()
        await test_db_session.refresh(status)
        
        assert status.id is not None
        assert status.report_id == report.id
        assert status.phase_name == "phase1"
        assert status.progress_percentage == 50.0


class TestReportRepository:
    """Test ReportRepository operations."""
    
    async def test_create_and_get_report(self, report_repository):
        """Test creating and retrieving a report."""
        report_data = {
            "game_id": "test-repo-game",
            "game_title": "Repository Test Game",
            "platform": "steam",
            "title": "Test Report",
            "markdown_content": "# Test\n\nContent here.",
            "json_content": {"test": True},
            "confidence_score": 0.8,
            "quality_rating": "fair",
            "word_count": 3,
            "data_completeness": 0.75,
            "status": "completed"
        }
        
        # Create report
        created_report = await report_repository.create_report(report_data)
        assert created_report.id is not None
        
        # Retrieve report
        retrieved_report = await report_repository.get_report_by_id(created_report.id)
        assert retrieved_report is not None
        assert retrieved_report.game_id == "test-repo-game"
        assert retrieved_report.title == "Test Report"
    
    async def test_get_reports_by_game_id(self, report_repository):
        """Test retrieving multiple reports for a game."""
        game_id = "multi-test-game"
        
        # Create multiple reports for same game
        for i in range(3):
            report_data = {
                "game_id": game_id,
                "game_title": f"Multi Test Game {i}",
                "platform": "steam",
                "title": f"Test Report {i}",
                "markdown_content": f"Content {i}",
                "json_content": {"report_num": i},
                "confidence_score": 0.8,
                "quality_rating": "good",
                "word_count": 2,
                "data_completeness": 0.8,
                "status": "completed"
            }
            await report_repository.create_report(report_data)
        
        # Retrieve all reports for the game
        reports = await report_repository.get_reports_by_game_id(game_id, limit=10)
        assert len(reports) == 3
        all_game_ids = [r.game_id for r in reports]
        assert all(gid == game_id for gid in all_game_ids)
    
    async def test_save_synthesis_result(self, report_repository):
        """Test saving synthesis results with metadata extraction."""
        master_json = {
            "executive_summary": "Game analysis complete",
            "metadata": {
                "completed_phases": ["phase1", "phase2", "phase3"],
                "overall_confidence": 0.92,
                "quality_rating": "excellent",
                "data_completeness": 0.95,
                "processing_time_ms": 2500
            },
            "analysis_data": {"key": "value"}
        }
        markdown_content = "# Game Analysis\n\nThis game is excellent."
        
        saved_report = await report_repository.save_synthesis_result(
            game_id="synthesis-test",
            game_title="Synthesis Test Game",
            platform="steam",
            master_json=master_json,
            markdown_content=markdown_content
        )
        
        assert saved_report.game_id == "synthesis-test"
        assert saved_report.summary == "Game analysis complete"
        assert saved_report.confidence_score == 0.92
        assert saved_report.quality_rating == "excellent"
        assert saved_report.data_completeness == 0.95
        assert saved_report.word_count == 6  # Count from markdown content
        assert saved_report.phases_completed == ["phase1", "phase2", "phase3"]
        assert saved_report.status == "completed"


class TestPipelineStatusRepository:
    """Test PipelineStatusRepository operations."""
    
    async def test_update_phase_status(self, pipeline_repository):
        """Test updating pipeline status for a phase."""
        # Create a test report first
        async for session in get_async_session():
            test_report = AnalysisReport(
                game_id="status-test-game",
                game_title="Status Test Game", 
                platform="steam",
                title="Status Test Report",
                markdown_content="Test",
                json_content={"test": True},
                status="pending"
            )
            session.add(test_report)
            await session.commit()
            await session.refresh(test_report)
            
            # Update phase status
            status = await pipeline_repository.update_phase_status(
                report_id=test_report.id,
                phase_name="phase1",
                status="running",
                progress=25.0
            )
            
            assert status.phase_name == "phase1"
            assert status.status == "running"
            assert status.progress_percentage == 25.0
            assert status.started_at is not None
            assert status.completed_at is None
        
        # Test completion
        async for session in get_async_session():
            completed_status = await pipeline_repository.update_phase_status(
                report_id=test_report.id,
                phase_name="phase1",
                status="completed",
                progress=100.0
            )
            
            assert completed_status.status == "completed"
            assert completed_status.progress_percentage == 100.0
            assert completed_status.completed_at is not None


class TestRawDataRepository:
    """Test RawDataRepository operations."""
    
    async def test_store_and_get_raw_data(self, raw_data_repository):
        """Test storing and retrieving raw analysis data."""
        game_id = "raw-data-test"
        
        # Store raw data
        content = {
            "scraped_data": {"screenshots": ["url1", "url2"]},
            "metadata": {"source": "steam"}
        }
        
        stored = await raw_data_repository.store_raw_data(
            game_id=game_id,
            phase="phase1",
            source="steam_scraper",
            data_type="screenshots",
            content=content,
            metadata={"scraper_version": "1.0"}
        )
        
        assert stored.id is not None
        assert stored.game_id == game_id
        assert stored.phase == "phase1"
        assert stored.data_type == "screenshots"
        
        # Retrieve stored data
        retrieved = await raw_data_repository.get_raw_data(game_id, phase="phase1")
        assert len(retrieved) >= 1
        assert retrieved[0].content["scraped_data"]["screenshots"] == ["url1", "url2"]


class TestReportService:
    """Test ReportService high-level operations."""
    
    async def test_create_new_report_and_track_progress(self, report_service):
        """Test creating a report and tracking pipeline progress."""
        game_id = "service-test-game"
        game_title = "Service Test Game"
        platform = "epic"
        
        # Create new report
        report = await report_service.create_new_report(game_id, game_title, platform)
        
        assert report.game_id == game_id
        assert report.status == "pending"
        assert report.total_phases == 4
        
        # Get pipeline status
        status_updates = await report_service.get_pipeline_status(report.id)
        assert len(status_updates) == 4  # Should have 4 phase statuses
        
        phase_names = [s.phase_name for s in status_updates]
        assert "phase1" in phase_names
        assert "phase2" in phase_names
        assert "phase3" in phase_names
        assert "phase4" in phase_names
        
        # Update progress
        success = await report_service.update_pipeline_progress(
            report.id, "phase1", "running", 0.0
        )
        assert success
        
        updated_status = await report_service.get_pipeline_status(report.id)
        phase1_status = next(s for s in updated_status if s.phase_name == "phase1")
        assert phase1_status.status == "running"
    
    async def test_save_complete_analysis_results(self, report_service):
        """Test saving complete analysis results through service."""
        report = await report_service.create_new_report(
            game_id="complete-analysis-test",
            game_title="Complete Analysis Game",
            platform="steam"
        )
        master_json = {
            "executive_summary": "Complete analysis finished successfully",
            "metadata": {
                "completed_phases": ["phase1", "phase2", "phase3"],
                "overall_confidence": 0.88,
                "quality_rating": "good",
                "data_completeness": 0.92,
                "processing_time_ms": 3500
            }
        }
        markdown_content = "# Complete Analysis\n\nFull report content here."
        
        saved_report = await report_service.save_analysis_results(
            report_id=report.id,
            game_id="complete-analysis-test",
            game_title="Complete Analysis Game",
            platform="steam",
            master_json=master_json,
            markdown_content=markdown_content
        )
        
        assert saved_report.status == "completed"
        assert saved_report.confidence_score == 0.88
        assert saved_report.word_count == 6
        
        # Verify pipeline status shows phase4 completed
        pipeline_status = await report_service.get_pipeline_status(saved_report.id)
        phase4_status = next(s for s in pipeline_status if s.phase_name == "phase4")
        assert phase4_status.status == "completed"


class TestIntegrationScenarios:
    """Integration tests that simulate real usage scenarios."""
    
    async def test_full_pipeline_simulation(self, report_service):
        """Simulate a full pipeline execution with database integration."""
        game_id = "full-pipeline-test"
        game_title = "Full Pipeline Test Game"
        platform = "steam"
        
        # 1. Create initial report
        report = await report_service.create_new_report(game_id, game_title, platform)
        report_id = report.id
        
        # 2. Simulate Phase 1 execution
        await report_service.update_pipeline_progress(report_id, "phase1", "running", 0.0)
        await report_service.store_phase_data(
            game_id, "phase1", "scrapers", "mini_contexts",
            {"design_art": {"data": "test"}, "user_experience": {"data": "test2"}},
            {"scraper_duration": 5.2}
        )
        await report_service.update_pipeline_progress(report_id, "phase1", "completed", 100.0)
        
        # 3. Simulate Phase 2 execution
        await report_service.update_pipeline_progress(report_id, "phase2", "running", 0.0)
        await report_service.store_phase_data(
            game_id, "phase2", "ai_analysis", "ai_analyses",
            [{"analysis_type": "design", "result": "good"}],
            {"ai_confidence": 0.85}
        )
        await report_service.update_pipeline_progress(report_id, "phase2", "completed", 100.0)
        
        # 4. Simulate Phase 3 execution
        await report_service.update_pipeline_progress(report_id, "phase3", "running", 0.0)
        await report_service.store_phase_data(
            game_id, "phase3", "synthesizer", "synthesis_result",
            {"word_count": 500, "status": "success"},
            {"synthesis_confidence": 0.90}
        )
        await report_service.update_pipeline_progress(report_id, "phase3", "completed", 100.0)
        
        # 5. Simulate Phase 4 - final database storage
        master_json = {
            "executive_summary": "Full pipeline completed successfully",
            "metadata": {
                "completed_phases": ["phase1", "phase2", "phase3"],
                "overall_confidence": 0.87,
                "quality_rating": "good",
                "data_completeness": 0.91,
                "processing_time_ms": 12000
            }
        }
        markdown_content = "# Full Pipeline Analysis\n\nComplete report with all phases integrated."
        
        final_report = await report_service.save_analysis_results(
            report_id=report_id,
            game_id=game_id,
            game_title=game_title,
            platform=platform,
            master_json=master_json,
            markdown_content=markdown_content
        )
        
        # 6. Verify final state
        assert final_report.status == "completed"
        assert final_report.confidence_score == 0.87
        
        pipeline_status = await report_service.get_pipeline_status(final_report.id)
        completed_phases = [s for s in pipeline_status if s.status == "completed"]
        assert len(completed_phases) == 4
        
        # 7. Test retrieval workflows
        latest_report = await report_service.get_latest_report_for_game(game_id)
        assert latest_report.id == final_report.id
        
        game_history = await report_service.get_game_analysis_history(game_id)
        assert len(game_history) == 1
        assert game_history[0]["game_id"] == game_id


if __name__ == "__main__":
    # Run specific test or all tests
    import sys
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        print(f"Running tests for {test_class}")
        # Implement test runner here
    else:
        print("Run with: pytest app/test_phase4_db_integration.py")