from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..models.user import User
from .security import verify_token

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    # Try to get token from Authorization header first
    token = credentials.credentials if credentials else None
    
    # If no header token, try cookie
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Special handling for demo user (by ID or demo flag)
    is_demo_user = (
        user_id == "00000000-0000-0000-0000-000000000001" or 
        payload.get("demo") is True
    )
    
    if is_demo_user:
        # Create mock user object for demo session
        from datetime import datetime
        import uuid
        
        demo_user = User()
        demo_user.id = uuid.UUID(user_id)
        demo_user.email = payload.get("email", "demo@getsmart.dev")
        demo_user.name = payload.get("name", "Demo User")
        demo_user.first_name = "Demo"
        demo_user.last_name = "User"
        demo_user.role = payload.get("role", "viewer")
        demo_user.avatar_url = None
        demo_user.avatar_initials = "DU"
        demo_user.department = None
        demo_user.sso_provider = "demo"
        demo_user.preferences = {
            "theme": "dark",
            "language": "en", 
            "notifications_email": True,
            "notifications_push": False
        }
        demo_user.created_at = datetime.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        demo_user.updated_at = None
        demo_user.last_login_at = datetime.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        demo_user.is_active = True
        
        return demo_user
    
    # Regular user lookup in database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    return user

def get_csrf_token(request: Request) -> str:
    csrf_token = request.cookies.get("csrf_token")
    if not csrf_token:
        from .security import generate_csrf_token
        csrf_token = generate_csrf_token()
    return csrf_token

async def verify_csrf_token(request: Request):
    if request.method in ["POST", "PATCH", "DELETE"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        cookie_token = request.cookies.get("csrf_token")
        
        if not csrf_token or csrf_token != cookie_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed"
            )
