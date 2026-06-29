from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, generate_csrf_token
import httpx
import json


class AuthService:
    
    @staticmethod
    async def get_sso_redirect_url(provider: str) -> str:
        """
        Get SSO redirect URL for the specified provider
        
        Args:
            provider: SSO provider (google, microsoft, okta)
            
        Returns:
            Redirect URL for SSO authorization
            
        Raises:
            HTTPException: If provider is not configured
        """
        if provider == "google":
            # In production, this would use Google's OAuth2 flow
            # For demo, return a mock URL
            return f"https://accounts.google.com/oauth/authorize?mock=true"
        elif provider == "microsoft":
            return f"https://login.microsoftonline.com/oauth/authorize?mock=true"
        elif provider == "okta":
            return f"https://okta.com/oauth/authorize?mock=true"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported SSO provider: {provider}"
            )
    
    @staticmethod
    async def exchange_code_for_tokens(provider: str, code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access tokens
        
        Args:
            provider: SSO provider name
            code: Authorization code from SSO provider
            
        Returns:
            Dictionary containing access_token and other token info
            
        Raises:
            HTTPException: If token exchange fails
        """
        # Mock implementation - in production, this would make actual HTTP requests
        try:
            # Simulate token exchange
            return {
                "access_token": f"mock_access_token_{code[:10]}",
                "refresh_token": f"mock_refresh_token_{code[:10]}",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token exchange failed: {str(e)}"
            )
    
    @staticmethod
    async def get_user_info(provider: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information from SSO provider using access token
        
        Args:
            provider: SSO provider name
            access_token: OAuth2 access token
            
        Returns:
            User information from the provider
            
        Raises:
            HTTPException: If user info retrieval fails
        """
        # Mock implementation - in production, this would make actual API calls
        try:
            if provider == "google":
                return {
                    "email": "demo@getsmart.dev",
                    "name": "Demo User",
                    "picture": "https://lh3.googleusercontent.com/mock-avatar.png",
                    "given_name": "Demo",
                    "family_name": "User"
                }
            elif provider == "microsoft":
                return {
                    "email": "demo@getsmart.dev",
                    "name": "Demo User",
                    "picture": "https://graph.microsoft.com/v1.0/me/photo/$value"
                }
            elif provider == "okta":
                return {
                    "email": "demo@getsmart.dev",
                    "name": "Demo User",
                    "picture": None
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown provider: {provider}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get user info: {str(e)}"
            )
    
    @staticmethod
    def create_demo_session() -> Dict[str, Any]:
        """Create demo user session"""
        demo_user_data = {
            "sub": "00000000-0000-0000-0000-000000000000",  # Fixed demo user ID
            "email": "demo@getsmart.dev",
            "name": "Demo User",
            "role": "viewer",
            "sso_provider": "demo"
        }
        
        access_token = create_access_token(demo_user_data)
        refresh_token = create_refresh_token({"sub": demo_user_data["sub"]})
        csrf_token = generate_csrf_token()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
            "user": demo_user_data
        }
    
    @staticmethod
    async def login_user(db: Session, user_info: Dict[str, Any], provider: str) -> User:
        """Create or update user from SSO provider info"""
        email = user_info.get("email")
        name = user_info.get("name", "")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        # Derive a username from the email local part
        username_base = email.split("@")[0]

        user = db.query(User).filter(User.email == email).first()

        default_settings = {
            "theme": "dark",
            "language": "en",
            "notifications_email": True,
            "notifications_push": False,
        }

        if not user:
            user = User(
                email=email,
                username=username_base,
                profile_jsonb={"display_name": name, "sso_provider": provider},
                settings_jsonb=default_settings,
                last_login_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            profile = dict(user.profile_jsonb or {})
            profile["display_name"] = name
            profile["sso_provider"] = provider
            user.profile_jsonb = profile
            user.last_login_at = datetime.utcnow()
            if not user.settings_jsonb:
                user.settings_jsonb = default_settings
            db.commit()
            db.refresh(user)

        return user