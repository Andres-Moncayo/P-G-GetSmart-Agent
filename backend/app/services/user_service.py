from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime
from ..models.user import User, ApiKey
from ..core.security import generate_api_key, hash_password

class UserService:
    
    @staticmethod
    def get_user_profile(db: Session, current_user: User) -> User:
        """Get current user's profile"""
        return current_user
    
    @staticmethod
    def update_user_profile(db: Session, current_user: User, updates: Dict[str, Any]) -> User:
        """Update user profile stored in profile_jsonb / settings_jsonb."""
        if "name" in updates:
            profile = dict(current_user.profile_jsonb or {})
            profile["display_name"] = updates["name"]
            current_user.profile_jsonb = profile

        if "preferences" in updates:
            settings = dict(current_user.settings_jsonb or {})
            settings.update(updates["preferences"])
            current_user.settings_jsonb = settings

        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        return current_user
    
    @staticmethod
    def get_api_keys(db: Session, current_user: User) -> List[ApiKey]:
        """Get user's API keys"""
        return db.query(ApiKey).filter(
            ApiKey.user_id == current_user.id,
            ApiKey.is_active == True
        ).all()
    
    @staticmethod
    def create_api_key(db: Session, current_user: User, name: str, scopes: List[str] = None) -> tuple[ApiKey, str]:
        """Create new API key"""
        if scopes is None:
            scopes = ["read"]
        
        full_key, prefix = generate_api_key()
        key_hash = hash_password(full_key)
        
        api_key = ApiKey(
            user_id=current_user.id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            scopes=scopes
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        return api_key, full_key
    
    @staticmethod
    def revoke_api_key(db: Session, current_user: User, key_id: UUID) -> bool:
        """Revoke API key"""
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id,
            ApiKey.is_active == True
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.is_active = False
        db.commit()
        return True
