from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .api.routes import router
from .api.skills_routes import skills_router
from .tasks.cache_manager import CacheManager
from .core.config import settings

app = FastAPI(title="GetSmart API", version="3.0.0")

app.include_router(router)
app.include_router(skills_router, prefix='/api')

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

@app.on_event("startup")
async def startup():
    await CacheManager.init_cache()

@app.get("/")
async def root():
    return {"message": "GetSmart API is running"}
