"""
Authentication service for handling OAuth user operations and response building.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import ValidationError
import json
from urllib.parse import urlencode

from ..database.models import User, OAuthProvider
from ..database.schemas import UserCreate, UserUpdate


def create_or_update_user(
    db: Session,
    email: str,
    name: Optional[str],
    avatar_url: Optional[str],
    provider: OAuthProvider
) -> User:
    """
    Create a new user or update existing user in the database.
    
    Args:
        db: Database session
        email: User email address
        name: User's full name
        avatar_url: URL to user's avatar/profile picture
        provider: OAuth provider (google/github)
    
    Returns:
        User: The created or updated user object
    
    Raises:
        HTTPException: If validation fails or database operation fails
    """
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Validate update data with Pydantic
            update_data = UserUpdate(
                name=name,
                avatar_url=avatar_url
            )
            # Update existing user info (only non-None values)
            if update_data.name:
                existing_user.name = update_data.name
            if update_data.avatar_url:
                existing_user.avatar_url = update_data.avatar_url
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # Validate new user data with Pydantic
            user_create = UserCreate(
                email=email,
                name=name,
                avatar_url=avatar_url,
                provider=provider
            )
            # Create new user from validated data
            new_user = User(**user_create.model_dump())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
            
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Data validation failed: {e.errors()}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")


def build_auth_response_data(
    user: User,
    id_token: Optional[str] = None,
    access_token: Optional[str] = None
) -> Dict:
    """
    Build structured authentication response data.
    
    Args:
        user: User database object
        id_token: OAuth ID token
        access_token: OAuth access token
    
    Returns:
        Dict: Structured user data with tokens
    """
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "provider": user.provider.value,
        "id_token": id_token,
        "access_token": access_token
    }


def build_frontend_redirect_url(
    frontend_url: str,
    response_data: Dict,
    path: str = "/auth/success"
) -> str:
    """
    Build frontend redirect URL with encoded user data.
    
    Args:
        frontend_url: Base frontend URL
        response_data: User data and tokens to encode
        path: Frontend path to redirect to (default: /auth/success)
    
    Returns:
        str: Complete redirect URL with encoded data parameter
    """
    params = urlencode({"data": json.dumps(response_data)})
    return f"{frontend_url}{path}?{params}"


def extract_user_info_from_oauth(
    user_info: Dict,
    provider: OAuthProvider
) -> Dict[str, Optional[str]]:
    """
    Extract standardized user information from OAuth provider response.
    
    Args:
        user_info: Raw user info from OAuth provider
        provider: OAuth provider type
    
    Returns:
        Dict with keys: email, name, avatar_url
    """
    if provider == OAuthProvider.GOOGLE:
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "avatar_url": user_info.get("picture")
        }
    elif provider == OAuthProvider.GITHUB:
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "avatar_url": user_info.get("avatar_url")
        }
    else:
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "avatar_url": None
        }
