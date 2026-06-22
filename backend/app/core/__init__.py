from typing import Annotated
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from uuid import UUID
from app.core.config import SECRET_KEY, ALGORITHM

security = HTTPBearer()  # For future JWT implementation, currently using cookies

async def get_current_user(
    session_cookie: str = Cookie(None, alias="session")
) -> UUID:
    """
    Get current user from session cookie
    Implements cookieAuth as specified in YAML endpoints
    """
    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode JWT from cookie (simplified implementation)
        payload = jwt.decode(session_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
            
        # Set user context for RLS
        from app.db.connection import engine
        async with engine.begin() as conn:
            await conn.execute(
                "SET app.current_user_id = :user_id",
                {"user_id": user_id}
            )
            
        return UUID(user_id)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )