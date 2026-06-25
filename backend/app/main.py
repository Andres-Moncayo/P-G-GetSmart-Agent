from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .api.skills_routes import skills_router
from .api.games_routes import games_router
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


@app.on_event("startup")
async def startup():
    await CacheManager.init_cache()
