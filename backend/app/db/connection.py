import os
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import ALGORITHM, SECRET_KEY

load_dotenv()


def _build_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL") or os.getenv("POSTGREST_URL", "")
    if not raw_url:
        return "postgresql+asyncpg://user:pass@localhost:5432/getsmarth"

    if raw_url.startswith("postgresql+asyncpg://"):
        normalized = raw_url
    elif raw_url.startswith("postgresql://"):
        normalized = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        parsed = urlparse(raw_url)
        if parsed.scheme in ("postgres", "postgresql"):
            normalized = urlunparse(parsed._replace(scheme="postgresql+asyncpg"))
        else:
            normalized = raw_url

    parsed = urlparse(normalized)
    query_params = dict(
        part.split("=", 1)
        for part in parsed.query.split("&")
        if "=" in part
    )
    requires_ssl = query_params.pop("sslmode", None) == "require"
    query_params.pop("channel_binding", None)
    clean_query = "&".join(f"{key}={value}" for key, value in query_params.items())
    return urlunparse(parsed._replace(query=clean_query)), requires_ssl


def _parse_database_config() -> tuple[str, dict]:
    url, requires_ssl = _build_database_url()
    connect_args = {"ssl": "require"} if requires_ssl else {}
    return url, connect_args


DATABASE_URL, CONNECT_ARGS = _parse_database_config()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

engine = create_async_engine(DATABASE_URL, echo=DEBUG, connect_args=CONNECT_ARGS)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_current_user_id(session_cookie: str = Cookie(None, alias="session")) -> UUID:
    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(session_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )
        return UUID(user_id)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )


async def get_db(
    current_user: UUID = Depends(get_current_user_id),
) -> AsyncSession:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"),
            {"user_id": str(current_user)},
        )
        yield session
