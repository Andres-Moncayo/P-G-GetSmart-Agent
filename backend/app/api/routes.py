from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.base import get_db
from app.models.user import User, ApiKey
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, verify_token, generate_csrf_token
from app.core.auth import get_current_user
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr

# ============================================================
# Request/Response Models
# ============================================================

class SsoLoginResponse(BaseModel):
    redirect_url: str

class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    avatar_initials: Optional[str] = None
    department: Optional[str] = None
    sso_provider: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: str
    updated_at: Optional[str] = None
    last_login_at: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[dict] = None

class ApiKeyCreate(BaseModel):
    name: str
    scopes: List[str] = ["read"]

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    scopes: List[str]
    created_at: str
    last_used_at: Optional[str] = None

class AccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int

class MessageResponse(BaseModel):
    message: str
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .macro_skills.design_art_skill.endpoints import router as design_art_router
from app.services import ReportService

from app.core import get_current_user
from app.db.connection import get_db
from app.models import (
    Facets,
    Report,
    ReportContentResponse,
    ReportListResponse,
    ReportUpdateRequest,
)

reports_router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

router = APIRouter()
router.include_router(reports_router)
router.include_router(design_art_router, prefix='/macro-skills/design-art', tags=['macro-skills'])


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    genre: list[str] | None = Query(None, alias="genre"),
    developer: list[str] | None = Query(None, alias="developer"),
    platform: list[str] | None = Query(None, alias="platform"),
    status: list[str] | None = Query(None, alias="status"),
    year_from: int | None = Query(None, ge=1980, le=2030, alias="year_from"),
    year_to: int | None = Query(None, ge=1980, le=2030, alias="year_to"),
    search: str | None = Query(None, max_length=100, alias="search"),
    sort_by: str | None = Query(
        "created_at",
        pattern=r"^(created_at|game\.name|game\.release_year|updated_at|progress_percent)$",
        alias="sort_by",
    ),
    sort_dir: str | None = Query("desc", pattern=r"^(asc|desc)$", alias="sort_dir"),
    page: int = Query(1, ge=1, alias="page"),
    page_size: int = Query(12, ge=1, le=50, alias="page_size"),
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    service = ReportService(db, current_user)
    return await service.list_reports(
        genre=genre,
        developer=developer,
        platform=platform,
        status=status,
        year_from=year_from,
        year_to=year_to,
        search=search,
        sort_by=sort_by or "created_at",
        sort_dir=sort_dir or "desc",
        page=page,
        page_size=page_size,
    )


@router.get("/facets", response_model=Facets)
async def get_filter_facets(
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user),
):
    service = ReportService(db, current_user)
    return await service.get_facets()


# ============================================================
# Authentication Endpoints
# ============================================================

@router.post('/api/v1/auth/login/{provider}', response_model=SsoLoginResponse)
async def login_provider(provider: str):
    """Initiate SSO login flow"""
    try:
        if provider not in ["google", "microsoft", "okta", "demo"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider. Must be one of: google, microsoft, okta, demo"
            )
        
        if provider == "demo":
            # For demo login, we don't need redirect URL
            # This endpoint is for SSO providers only
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use POST /api/v1/auth/demo for demo login"
            )
        
        redirect_url = await AuthService.get_sso_redirect_url(provider)
        return SsoLoginResponse(redirect_url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO configuration error"
        )

@router.post('/api/v1/auth/demo')
async def demo_login(response: Response):
    """Login with demo account"""
    try:
        # Create bulletproof demo user data exact match to OpenAPI schema
        demo_user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "demo@getsmart.dev",  # Use contract's demo email
            "name": "Demo User",  # Use contract's demo name
            "first_name": "Demo",
            "last_name": "User",
            "role": "viewer",  # Use contract's demo role
            "avatar_url": None,  # Allow null as per schema
            "avatar_initials": "DU",  # Use contract's demo initials
            "department": None,  # Allow null as per schema  
            "sso_provider": "demo",
            "preferences": {
                "theme": "dark",  # Use contract default theme
                "language": "en",  # Use contract default language
                "notifications_email": True,  # Use contract default
                "notifications_push": False   # Use contract default
            },
            "created_at": "2024-01-01T00:00:00Z",  # Required field, ISO 8601
            "updated_at": None,  # Allow null as per schema
            "last_login_at": "2024-01-01T00:00:00Z"  # ISO 8601 timestamp
        }
        
        # Create tokens using actual app security functions only
        # NO FALLBACK TO MOCK TOKENS - this was causing the 401 errors!
        
        # Create proper session data for tokens
        session_data = {
            "sub": demo_user["id"],
            "email": demo_user["email"],
            "name": demo_user["name"],
            "role": demo_user["role"],
            "user_id": demo_user["id"],  # Add user_id for demo detection
            "demo": True  # Mark as demo token
        }
        
        # Create tokens using real app configuration ONLY
        access_token = create_access_token(session_data)
        refresh_token = create_refresh_token({"sub": demo_user["id"], "demo": True})
        csrf_token = generate_csrf_token()
        
        # Set secure cookies (disable secure for development)
        is_development = True  # You can make this configurable
        
        cookie_settings = {
            "max_age": 3600,
            "httponly": True,
            "secure": not is_development,
            "samesite": "strict"
        }
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            **cookie_settings
        )
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token,
            max_age=604800,  # 7 days
            httponly=True,
            secure=not is_development,
            samesite="strict",
            path="/api/v1/auth/refresh"
        )
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            **cookie_settings
        )
        
        # Return success response matching contract schema
        return {
            "message": "Demo session created successfully",
            "access_token": access_token,
            "expires_in": 3600,
            "token_type": "Bearer",
            "user": demo_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # If token creation fails, raise proper error - don't use fallback tokens!
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create demo session: {str(e)}"
        )

@router.get('/api/v1/auth/callback/{provider}')
async def auth_callback(provider: str, code: str, state: str, db: Session = Depends(get_db)):
    """Handle SSO callback and create session"""
    try:
        if provider not in ["google", "microsoft", "okta"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider"
            )
        
        # Exchange code for tokens
        tokens = await AuthService.exchange_code_for_tokens(provider, code)
        
        # Get user info
        user_info = await AuthService.get_user_info(provider, tokens["access_token"])
        
        # Create/update user
        user = await AuthService.login_user(db, user_info, provider)
        
        # Create session
        session_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        
        access_token = create_access_token(session_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        csrf_token = generate_csrf_token()
        
        response = RedirectResponse(url="/", status_code=302)
        
        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite="strict"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=604800,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/api/v1/auth/refresh"
        )
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite="strict"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token exchange failed"
        )

@router.post('/api/v1/auth/logout', response_model=MessageResponse)
async def logout(response: Response):
    """Invalidate session and clear cookies"""
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/v1/auth/refresh"
    )
    response.delete_cookie(
        key="csrf_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return MessageResponse(message="Session terminated")

@router.post('/api/v1/auth/refresh', response_model=AccessTokenResponse)
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Special handling for demo user
    is_demo_user = (
        user_id == "00000000-0000-0000-0000-000000000001" or 
        payload.get("demo") is True
    )
    
    if is_demo_user:
        # Create new access token for demo user
        session_data = {
            "sub": user_id,
            "email": "demo@getsmart.dev",
            "name": "Demo User",
            "role": "viewer",
            "user_id": user_id,
            "demo": True
        }
        
        new_access_token = create_access_token(session_data)
        
        return AccessTokenResponse(
            access_token=new_access_token,
            expires_in=3600
        )
    
    # Regular user lookup in database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    session_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role
    }
    
    new_access_token = create_access_token(session_data)
    
    return AccessTokenResponse(
        access_token=new_access_token,
        expires_in=3600
    )

# ============================================================
# User Profile Endpoints
# ============================================================

@router.get('/api/v1/me', response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        avatar_url=current_user.avatar_url,
        avatar_initials=current_user.avatar_initials,
        department=current_user.department,
        sso_provider=current_user.sso_provider,
        preferences=current_user.preferences,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None,
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )

@router.patch('/api/v1/me', response_model=UserProfileResponse)
async def update_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        update_data = {}
        if updates.name is not None:
            update_data["name"] = updates.name
        if updates.preferences is not None:
            update_data["preferences"] = updates.preferences
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        updated_user = UserService.update_user_profile(db, current_user, update_data)
        
        return UserProfileResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            name=updated_user.name,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            role=updated_user.role,
            avatar_url=updated_user.avatar_url,
            avatar_initials=updated_user.avatar_initials,
            department=updated_user.department,
            sso_provider=updated_user.sso_provider,
            preferences=updated_user.preferences,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else "",
            updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else None,
            last_login_at=updated_user.last_login_at.isoformat() if updated_user.last_login_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get('/api/v1/me/api-keys', response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    try:
        api_keys = UserService.get_api_keys(db, current_user)
        return [
            ApiKeyResponse(
                id=str(key.id),
                name=key.name,
                prefix=key.prefix,
                scopes=key.scopes,
                created_at=key.created_at.isoformat() if key.created_at else "",
                last_used_at=key.last_used_at.isoformat() if key.last_used_at else None
            )
            for key in api_keys
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys"
        )

@router.post('/api/v1/me/api-keys', response_model=dict)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate new API key"""
    try:
        api_key, full_key = UserService.create_api_key(db, current_user, key_data.name, key_data.scopes)
        
        return {
            "id": str(api_key.id),
            "name": api_key.name,
            "key": full_key,  # Only shown once
            "prefix": api_key.prefix,
            "scopes": api_key.scopes,
            "created_at": api_key.created_at.isoformat() if api_key.created_at else ""
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )

@router.delete('/api/v1/me/api-keys/{key_id}', status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke API key"""
    try:
        key_uuid = UUID(key_id)
        UserService.revoke_api_key(db, current_user, key_uuid)
        return None
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid API key ID"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key"
        )
