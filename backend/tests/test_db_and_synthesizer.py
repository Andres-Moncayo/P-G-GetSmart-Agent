import pytest
import uuid
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
from sqlalchemy import text
from app.db.connection import AsyncSessionLocal

@pytest.mark.asyncio
async def test_full_db_and_synthesizer_flow():
    # 1. TABLE INVENTORY
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"))
        tables = {row[0] for row in result.fetchall()}
    expected = {"users", "roles", "analysis", "reports"}
    missing = expected - tables
    assert not missing, f"Missing tables: {missing}"

    # 2. COLUMN ALIGNMENT
    checks = {
        "users":   ["id","email","username","password_hash","is_verified","is_active","created_at","updated_at","last_login_at","timezone","language","profile_jsonb","settings_jsonb"],
        "roles":   ["id","user_id","role_name","is_active"],
        "analysis":["id","user_id","game_id","analysis_type","status","confidence_score","input_data_jsonb","raw_output_jsonb","processed_output_jsonb","metrics_jsonb","error_details_jsonb","final_report_id","created_at","completed_at"],
        "reports": ["id","user_id","game_id","report_status","report_type","game_name","cover_url","all_genres","all_platforms","current_phase","pipeline_progress","markdown_content","confidence_score","executive_summary_jsonb","thematic_analysis_jsonb","strategic_recommendations_jsonb","game_data_jsonb"],
    }
    async with AsyncSessionLocal() as db:
        for table, expected_cols in checks.items():
            result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = :t"), {"t": table})
            db_cols = {row[0] for row in result.fetchall()}
            missing = [c for c in expected_cols if c not in db_cols]
            assert not missing, f"'{table}' missing columns: {missing}"

    # 3. DEMO USER
    DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT id, email, username FROM users WHERE id = :uid"), {"uid": DEMO_USER_ID})
        row = result.first()
    assert row is not None, f"Demo user '{DEMO_USER_ID}' NOT found"

    # 4. create_new_report
    from app.services.report_service import ReportService
    svc = ReportService()
    test_game = f"Test Game {uuid.uuid4().hex[:6]}"
    report = await svc.create_new_report(
        game_id=str(uuid.uuid4()),
        game_name=test_game,
        platform="PC",
        developer_name="Test Studio",
        release_year=2024,
        primary_genre="Action",
        primary_platform="PC",
        all_genres=["Action", "Adventure"],
        all_platforms=["PC", "PlayStation 5"],
        cover_url="https://example.com/cover.jpg",
    )
    report_id = str(report.id)

    # 5. save_analysis_results
    master_json = {
        "executive_summary": {"game_identity": "Test Game", "market_position": "Test market position", "key_insights": ["insight 1"]},
        "thematic_analysis": {"themes": []},
        "cross_cutting_insights": {},
        "strategic_recommendations": {"recommendations": []},
        "risk_assessment": {"risks": []},
        "appendices": {},
        "confidence_analysis": {},
        "synthesis": {"synthesis_confidence": 0.85},
        "metadata": {"overall_confidence": 0.85, "pipeline_version": "3.0.0", "synthesis_model": "test"},
    }
    report_updated = await svc.save_analysis_results(
        report_id=report_id,
        game_id=str(uuid.uuid4()),
        game_name="Test Game",
        platform="PC",
        master_json=master_json,
        markdown_content="# Test Report\n",
        ai_results={
            "design_art": {"raw": "design art data"},
            "user_experience": {"raw": "ux data"},
            "technology_systems": {"raw": "tech data"},
            "strategy_market": {"raw": "strategy data"},
        },
    )
    assert report_updated is not None
    assert report_updated.report_status == "completed"

    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT analysis_type, status FROM analysis WHERE final_report_id = :rid ORDER BY analysis_type"), {"rid": report_id})
        rows = result.fetchall()
    assert len(rows) > 0, "No analysis rows were created"

    # 6. list_reports
    from app.services import ReportService as DashReportService
    async with AsyncSessionLocal() as db:
        dash_svc = DashReportService(db=db, user_id=None)
        response = await dash_svc.list_reports(page=1, page_size=5)
        assert response is not None
        assert hasattr(response, 'pagination')
        assert hasattr(response, 'items')
        assert hasattr(response, 'facets')

    # Cleanup
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("DELETE FROM analysis WHERE final_report_id = :rid"), {"rid": report_id})
            await db.execute(text("DELETE FROM reports WHERE id = :rid"), {"rid": report_id})
            await db.commit()
    except Exception as e:
        print(f"Cleanup failed: {e}")
