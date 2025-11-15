from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.oauth import (
    get_github_authorize_url,
    exchange_github_code_for_tokens,
    get_github_userinfo
)
from ..database.connection import get_db
from ..database.models import OAuthProvider
from ..services.auth_service import (
    create_or_update_user,
    build_auth_response_data,
    build_frontend_redirect_url,
    extract_user_info_from_oauth
)

router = APIRouter(
    tags=["auth_github"],
    prefix="/auth/github",
)


@router.get("")
async def auth_github(request: Request):
    """
    Initiate GitHub OAuth flow.
    Redirects the user to GitHub's OAuth authorization page.
    """
    # Validate GitHub credentials are configured
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID in environment variables."
        )
    
    redirect_uri = f"{settings.BACKEND_HOST}/auth/github/callback"
    url = get_github_authorize_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/callback")
async def auth_github_callback(
    request: Request, 
    code: str = None, 
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    GitHub OAuth callback endpoint.
    Exchanges authorization code for tokens and creates/updates user.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    redirect_uri = f"{settings.BACKEND_HOST}/auth/github/callback"

    # Exchange code for tokens
    try:
        token_response = exchange_github_code_for_tokens(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {e}")

    access_token = token_response.get("access_token")

    # Fetch user info from GitHub
    user_info = {}
    try:
        if access_token:
            user_info = get_github_userinfo(access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user info: {e}")

    # Extract standardized user data
    extracted_info = extract_user_info_from_oauth(user_info, OAuthProvider.GITHUB)
    
    if not extracted_info["email"]:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    # Create or update user in database
    db_user = create_or_update_user(
        db=db,
        email=extracted_info["email"],
        name=extracted_info["name"],
        avatar_url=extracted_info["avatar_url"],
        provider=OAuthProvider.GITHUB
    )

    # Build response data with user info and tokens
    response_data = build_auth_response_data(
        user=db_user,
        id_token=None,  # GitHub doesn't use id_token
        access_token=access_token
    )

    # Build frontend redirect URL
    redirect_url = build_frontend_redirect_url(settings.FRONTEND_URL, response_data)

    return RedirectResponse(redirect_url)
