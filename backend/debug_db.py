import asyncio
import sys
import os
import traceback
from dotenv import load_dotenv

# Add the app path
sys.path.append('.')

load_dotenv()

print(f"DATABASE_URL loaded: {bool(os.getenv('DATABASE_URL'))}")

try:
    from app.db.connection import engine
    from sqlalchemy import text

    async def test_database():
        print("Testing database connection...")
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text('SELECT version()'))
                version = result.scalar()
                print(f'PostgreSQL connected: {version[:50]}...')
                
                result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'reports'"))
                rows = result.fetchall()
                print(f'Reports table exists: {len(rows) > 0}')
                
                if len(rows) > 0:
                    count_result = await conn.execute(text('SELECT COUNT(*) FROM reports'))
                    count = count_result.scalar()
                    print(f'Total reports: {count}')
                    
                    # Get a sample report
                    sample = await conn.execute(text('SELECT id, game_name, report_status FROM reports LIMIT 1'))
                    sample_row = sample.first()
                    if sample_row:
                        print(f'Sample report: {sample_row.id} - {sample_row.game_name} ({sample_row.report_status})')
                else:
                    print('Reports table does not exist!')
                    
        except Exception as e:
            print(f'Database connection error: {e}')
            traceback.print_exc()

    if __name__ == "__main__":
        asyncio.run(test_database())
        
except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()