from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .api.skills_routes import skills_router
from .api.games_routes import games_router
from .api.reports_routes import reports_router
from .services.scraper.presentation.api import router as scraper_router
from .tasks.cache_manager import CacheManager
from .core.config import settings

app = FastAPI(title="GetSmart API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(skills_router, prefix="/api")
app.include_router(games_router)
app.include_router(reports_router)
app.include_router(scraper_router, prefix="/scraper")


@app.on_event("startup")
async def startup():
    from .db.connection import check_database_connection
    is_online = await check_database_connection()
    if is_online:
        print("DATABASE STATUS: ONLINE")
    else:
        print("DATABASE STATUS: OFFLINE. Running in Mock Mode fallback!")
    await CacheManager.init_cache()
