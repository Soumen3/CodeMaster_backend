from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.oauth import get_google_authorize_url, exchange_code_for_tokens, get_userinfo
from ..database.connection import get_db
from ..database.models import OAuthProvider
from ..services.auth_service import (
    create_or_update_user,
    build_auth_response_data,
    build_frontend_redirect_url,
    extract_user_info_from_oauth
)

router = APIRouter(
    tags=["auth_google"],
    prefix="/auth/google",
)


@router.get("")
async def auth_google(request: Request):
    """
    Initiate Google OAuth flow.
    Redirects the user to Google's OAuth consent screen.
    """
    redirect_uri = f"{settings.BACKEND_HOST}/auth/google/callback"
    url = get_google_authorize_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/callback")
async def auth_google_callback(
    request: Request, 
    code: str = None, 
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Google OAuth callback endpoint.
    Exchanges authorization code for tokens and creates/updates user.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    redirect_uri = f"{settings.BACKEND_HOST}/auth/google/callback"

    # Exchange code for tokens
    try:
        token_response = exchange_code_for_tokens(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {e}")

    access_token = token_response.get("access_token")
    id_token = token_response.get("id_token")

    # Fetch user info from Google
    user_info = {}
    try:
        if access_token:
            user_info = get_userinfo(access_token)
    except Exception:
        user_info = {}

    # Extract standardized user data
    extracted_info = extract_user_info_from_oauth(user_info, OAuthProvider.GOOGLE)
    
    if not extracted_info["email"]:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    # Create or update user in database
    db_user = create_or_update_user(
        db=db,
        email=extracted_info["email"],
        name=extracted_info["name"],
        avatar_url=extracted_info["avatar_url"],
        provider=OAuthProvider.GOOGLE
    )

    # Build response data with user info and tokens
    response_data = build_auth_response_data(
        user=db_user,
        id_token=id_token,
        access_token=access_token
    )

    # Build frontend redirect URL
    redirect_url = build_frontend_redirect_url(settings.FRONTEND_URL, response_data)

    return RedirectResponse(redirect_url)
