from fastapi import FastAPI
from .api.routes import router

app = FastAPI()
app.include_router(router, prefix='/api')


@app.on_event("startup")
async def startup():
    """Initialize FastAPI in-memory caching."""
    # Cache initialization pending
    pass
