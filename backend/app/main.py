from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .api.routes import router
from .tasks.cache_manager import CacheManager
from .core.config import settings

app = FastAPI(
    title="GetSmart API",
    description="Game Intelligence Library API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# Include routers
app.include_router(router)

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

@app.on_event("startup")
async def startup():
    """Initialize FastAPI in-memory caching."""
    await CacheManager.init_cache()

@app.get("/")
async def root():
    return {"message": "GetSmart API is running"}