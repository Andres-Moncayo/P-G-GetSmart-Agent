"""
Verification script — runs against the live Neon DB.

Checks:
  1. Which tables exist (and detects leftover tables from old create_all)
  2. Column alignment: models vs actual DB columns
  3. Demo-user row exists (required for pipeline user_id FK)
  4. ReportService.create_new_report() inserts a real row
  5. ReportService.save_analysis_results() updates the row + writes Analysis rows
  6. GET /api/v1/reports query (via ReportService from services/__init__.py)
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("ENVIRONMENT", "development")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from sqlalchemy import text
from app.db.connection import AsyncSessionLocal, engine


# ── helpers ──────────────────────────────────────────────────────────────────

GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW = "\033[93m"
CYAN  = "\033[96m"
RESET = "\033[0m"

def ok(msg):    print(f"  {GREEN}[OK]{RESET} {msg}")
def fail(msg):  print(f"  {RED}[FAIL]{RESET} {msg}")
def warn(msg):  print(f"  {YELLOW}[WARN]{RESET} {msg}")
def info(msg):  print(f"  {CYAN}[INFO]{RESET} {msg}")
def section(s): print(f"\n{CYAN}{'='*60}{RESET}\n  {s}\n{CYAN}{'='*60}{RESET}")


# ── 1. Table inventory ────────────────────────────────────────────────────────

async def check_tables():
    section("1. TABLE INVENTORY")
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        tables = {row[0] for row in result.fetchall()}

    expected = {"users", "roles", "analysis", "reports"}
    old_names = {"analysis_reports", "pipeline_status", "raw_analysis_data", "api_keys"}

    for t in sorted(tables):
        if t in expected:
            ok(f"'{t}' — expected table present")
        elif t in old_names:
            warn(f"'{t}' — OLD table still in DB (created by old create_all, safe to drop)")
        else:
            info(f"'{t}' — extra table (not in UnityGsmart.sql, may be from extensions/views)")

    missing = expected - tables
    for t in missing:
        fail(f"'{t}' — MISSING from DB, apply UnityGsmart.sql!")

    return expected.issubset(tables)


# ── 2. Column alignment ───────────────────────────────────────────────────────

async def check_columns():
    section("2. COLUMN ALIGNMENT (models vs DB)")

    checks = {
        "users":   ["id","email","username","password_hash","is_verified","is_active",
                    "created_at","updated_at","last_login_at","timezone","language",
                    "profile_jsonb","settings_jsonb"],
        "roles":   ["id","user_id","role_name","is_active"],
        "analysis":["id","user_id","game_id","analysis_type","status","confidence_score",
                    "input_data_jsonb","raw_output_jsonb","processed_output_jsonb",
                    "metrics_jsonb","error_details_jsonb","final_report_id",
                    "created_at","completed_at"],
        "reports": ["id","user_id","game_id","report_status","report_type","game_name",
                    "cover_url","all_genres","all_platforms","current_phase",
                    "pipeline_progress","markdown_content","confidence_score",
                    "executive_summary_jsonb","thematic_analysis_jsonb",
                    "strategic_recommendations_jsonb","game_data_jsonb"],
    }

    all_ok = True
    async with AsyncSessionLocal() as db:
        for table, expected_cols in checks.items():
            result = await db.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :t
            """), {"t": table})
            db_cols = {row[0] for row in result.fetchall()}

            missing = [c for c in expected_cols if c not in db_cols]
            if missing:
                fail(f"'{table}' missing columns: {missing}")
                all_ok = False
            else:
                ok(f"'{table}' — all {len(expected_cols)} checked columns present")

    return all_ok


# ── 3. Demo user ──────────────────────────────────────────────────────────────

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

async def check_demo_user():
    section("3. DEMO USER")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT id, email, username FROM users WHERE id = :uid"),
            {"uid": DEMO_USER_ID}
        )
        row = result.first()

    if row:
        ok(f"Demo user exists — email={row.email}, username={row.username}")
        return True
    else:
        fail(f"Demo user '{DEMO_USER_ID}' NOT found — apply UnityGsmart.sql seed")
        return False


# ── 4. ReportService.create_new_report ───────────────────────────────────────

async def test_create_report():
    section("4. create_new_report() -- INSERT into `reports`")
    from app.services.report_service import ReportService

    svc = ReportService()
    test_game = f"Test Game {uuid.uuid4().hex[:6]}"
    try:
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
        ok(f"Row created — id={report.id}")
        ok(f"report_status='{report.report_status}', game_name='{report.game_name}'")
        ok(f"cover_url='{report.cover_url}'")
        ok(f"current_phase='{report.current_phase}', pipeline_progress={report.pipeline_progress}")
        return str(report.id)
    except Exception as exc:
        fail(f"create_new_report failed: {exc}")
        return None
    finally:
        await svc.close()


# ── 5. ReportService.save_analysis_results ───────────────────────────────────

async def test_save_analysis(report_id: str):
    section("5. save_analysis_results() -- UPDATE reports + INSERT analysis rows")
    if not report_id:
        warn("Skipped — no report_id from step 4")
        return False

    from app.services.report_service import ReportService

    # Minimal master_json matching the synthesizer output shape
    master_json = {
        "executive_summary": {
            "game_identity": "Test Game — synthetic data",
            "market_position": "Test market position",
            "key_insights": ["insight 1", "insight 2"],
        },
        "thematic_analysis": {"themes": []},
        "cross_cutting_insights": {},
        "strategic_recommendations": {"recommendations": []},
        "risk_assessment": {"risks": []},
        "appendices": {},
        "confidence_analysis": {},
        "synthesis": {"synthesis_confidence": 0.85},
        "metadata": {
            "overall_confidence": 0.85,
            "pipeline_version": "3.0.0",
            "synthesis_model": "test",
        },
    }
    markdown = "# Test Report\n\nThis is a test markdown report generated by the verification script.\n"

    svc = ReportService()
    try:
        report = await svc.save_analysis_results(
            report_id=report_id,
            game_id=str(uuid.uuid4()),
            game_name="Test Game",
            platform="PC",
            master_json=master_json,
            markdown_content=markdown,
            ai_results={
                "design_art": {"raw": "design art data"},
                "user_experience": {"raw": "ux data"},
                "technology_systems": {"raw": "tech data"},
                "strategy_market": {"raw": "strategy data"},
            },
        )
        if report:
            ok(f"reports row updated — report_status='{report.report_status}'")
            ok(f"confidence_score={report.confidence_score}")
            ok(f"markdown_content length={len(report.markdown_content or '')} chars")
            ok(f"pipeline_progress={report.pipeline_progress}")
        else:
            fail("save_analysis_results returned None — report row may not exist")
            return False

        # Verify analysis rows were inserted
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text("SELECT analysis_type, status FROM analysis WHERE final_report_id = :rid ORDER BY analysis_type"),
                {"rid": report_id}
            )
            rows = result.fetchall()
        if rows:
            ok(f"Analysis rows created: {[(r.analysis_type, r.status) for r in rows]}")
        else:
            warn("No analysis rows found (DB constraint may have blocked — check FK on final_report_id)")
        return True

    except Exception as exc:
        fail(f"save_analysis_results failed: {exc}")
        import traceback; traceback.print_exc()
        return False
    finally:
        await svc.close()


# ── 6. Dashboard list query ───────────────────────────────────────────────────

async def test_list_reports():
    section("6. ReportService.list_reports() — dashboard query")
    from app.services import ReportService as DashReportService

    async with AsyncSessionLocal() as db:
        svc = DashReportService(db=db, user_id=None)
        try:
            response = await svc.list_reports(page=1, page_size=5)
            ok(f"total={response.pagination.total} reports in DB")
            ok(f"Page 1 returned {len(response.items)} items")
            if response.items:
                r = response.items[0]
                ok(f"First item: game='{r.game.name}', status='{r.status}'")
            ok(f"Facets: {len(response.facets.status)} status values, {len(response.facets.genre)} genres")
            return True
        except Exception as exc:
            fail(f"list_reports failed: {exc}")
            import traceback; traceback.print_exc()
            return False


# ── 7. Cleanup test report ────────────────────────────────────────────────────

async def cleanup(report_id: str):
    if not report_id:
        return
    section("7. CLEANUP — deleting test rows")
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(
                text("DELETE FROM analysis WHERE final_report_id = :rid"),
                {"rid": report_id}
            )
            await db.execute(
                text("DELETE FROM reports WHERE id = :rid"),
                {"rid": report_id}
            )
            await db.commit()
            ok(f"Deleted test report {report_id} and its analysis rows")
        except Exception as exc:
            warn(f"Cleanup failed (manual delete may be needed): {exc}")


# ── main ──────────────────────────────────────────────────────────────────────

async def main():
    print(f"\n{CYAN}GetSmart DB + Synthesizer Verification{RESET}")
    print(f"DB: Neon / getsmarth")
    print(f"Time: {datetime.now().isoformat()}")

    results = {}

    results["tables"]      = await check_tables()
    results["columns"]     = await check_columns()
    results["demo_user"]   = await check_demo_user()

    report_id = await test_create_report()
    results["create"]      = report_id is not None
    results["save"]        = await test_save_analysis(report_id)
    results["list"]        = await test_list_reports()

    await cleanup(report_id)

    # Summary
    section("SUMMARY")
    all_passed = True
    for name, passed in results.items():
        if passed:
            ok(f"{name}")
        else:
            fail(f"{name}")
            all_passed = False

    print()
    if all_passed:
        print(f"{GREEN}All checks passed — backend + DB fully aligned.{RESET}\n")
    else:
        print(f"{RED}Some checks failed — see details above.{RESET}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
