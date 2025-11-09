from fastapi import APIRouter, Depends
from ..core.security import get_current_user, get_current_user_optional
from ..database.models import User
from typing import Optional

router = APIRouter(
    tags=["auth"],
    prefix="/auth",
)


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Requires authentication.
    
    Returns:
        User information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "provider": current_user.provider.value,
        "created_at": current_user.created_at
    }


@router.get("/check")
async def check_auth_status(current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Check authentication status without requiring authentication.
    Returns user info if authenticated, otherwise returns guest status.
    
    Returns:
        Authentication status and user info if available
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "avatar_url": current_user.avatar_url
            }
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }
