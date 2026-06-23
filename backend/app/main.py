from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as reports_router
from .api.skills_routes import skills_router
from .tasks.cache_manager import CacheManager

app = FastAPI(title="GetSmart API", version="3.0.0")

# Reports endpoints: /api/v1/reports/*
app.include_router(reports_router, prefix='/api')

# Skills endpoints: /api/skills/*  
app.include_router(skills_router, prefix='/api')

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
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
    """Initialize FastAPI in-memory caching."""
    await CacheManager.init_cache()
