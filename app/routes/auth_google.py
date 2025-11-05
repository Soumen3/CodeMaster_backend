from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import os

from ..core.oauth import get_google_authorize_url, exchange_code_for_tokens, get_userinfo

router = APIRouter()


@router.get("/auth/google")
async def auth_google(request: Request):
    # Redirect the user to Google's OAuth consent screen
    backend_host = os.getenv("BACKEND_HOST", "http://localhost:8000")
    redirect_uri = f"{backend_host}/auth/google/callback"
    url = get_google_authorize_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/auth/google/callback")
async def auth_google_callback(request: Request, code: str = None, state: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    backend_host = os.getenv("BACKEND_HOST", "http://localhost:8000")
    redirect_uri = f"{backend_host}/auth/google/callback"

    try:
        token_response = exchange_code_for_tokens(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {e}")

    # token_response may contain access_token, id_token, refresh_token
    access_token = token_response.get("access_token")
    id_token = token_response.get("id_token")

    user = {}
    try:
        if access_token:
            user = get_userinfo(access_token)
    except Exception:
        # ignore userinfo failure, proceed with tokens
        user = {}

    # Build redirect to frontend including id_token (if available) as query param
    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
    params = []
    if id_token:
        params.append(f"id_token={id_token}")
    if access_token and not id_token:
        params.append(f"access_token={access_token}")

    # optionally include basic user info (not secure for production)
    if user.get("email"):
        params.append(f"email={user.get('email')}")

    q = "&".join(params)
    dest = f"{frontend}/auth/success"
    if q:
        dest = f"{dest}?{q}"

    return RedirectResponse(dest)
