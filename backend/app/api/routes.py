from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

# Simple router for basic functionality
router = APIRouter()

# Models
class HealthResponse(BaseModel):
    status: str

class MessageResponse(BaseModel):
    message: str

# Basic endpoints
@router.get("/", response_model=dict)
async def root():
    return {"message": "GetSmart API is running"}

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")

@router.post("/api/v1/auth/demo", response_model=dict)
async def demo_login(response: Response):
    """Simple demo login"""
    return {
        "message": "Demo session created successfully",
        "access_token": "demo_token_12345",
        "expires_in": 3600,
        "token_type": "Bearer",
        "user": {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "demo@getsmart.dev",
            "name": "Demo User",
            "role": "viewer"
        }
    }

@router.post("/api/v1/auth/logout", response_model=MessageResponse)
async def logout():
    """Logout endpoint"""
    return MessageResponse(message="Session terminated")