from fastapi import FastAPI
from .api.routes import router
from .tasks.cache_manager import CacheManager

app = FastAPI()
app.include_router(router, prefix='/api')


@app.on_event("startup")
async def startup():
    """Initialize FastAPI in-memory caching."""
    await CacheManager.init_cache()
