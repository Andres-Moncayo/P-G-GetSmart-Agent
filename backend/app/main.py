from fastapi import FastAPI
from .api.routes import router
from .api.skills_routes import skills_router
from .tasks.cache_manager import CacheManager

app = FastAPI(title="GetSmart API", version="3.0.0")

app.include_router(router, prefix='/api')
app.include_router(skills_router, prefix='/api')


@app.on_event("startup")
async def startup():
    """Initialize FastAPI in-memory caching."""
    # Cache initialization pending
    pass
