from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .api.routes import router
from .api.skills_routes import skills_router
from .api.games_routes import games_router
from .tasks.cache_manager import CacheManager
from .core.config import settings

app = FastAPI(title="GetSmart API", version="3.0.0")

app.include_router(router)
app.include_router(skills_router, prefix='/api')
app.include_router(games_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "GetSmart Agent API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    await CacheManager.init_cache()

@app.get("/")
async def root():
    return {"message": "GetSmart API is running"}
