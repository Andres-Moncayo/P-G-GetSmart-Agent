from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://neondb_owner:npg_QZN5qMuUjv9h@ep-misty-sky-aqh6wq9v-pooler.c-8.us-east-1.aws.neon.tech//getsmarth?sslmode=require&channel_binding=required')
DEBUG=True
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session