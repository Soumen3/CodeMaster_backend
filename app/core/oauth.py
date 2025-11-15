from typing import Optional
import requests
from .config import settings

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"


def get_google_authorize_url(redirect_uri: str, state: Optional[str] = None) -> str:
    client_id = settings.GOOGLE_CLIENT_ID
    scope = "openid email profile"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    # build query string
    from urllib.parse import urlencode

    return f"{GOOGLE_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    resp = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_userinfo(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(GOOGLE_USERINFO, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


# GitHub OAuth functions
def get_github_authorize_url(redirect_uri: str, state: Optional[str] = None) -> str:
    """
    Build GitHub OAuth authorization URL.
    
    Args:
        redirect_uri: Callback URL for OAuth redirect
        state: Optional state parameter for CSRF protection
    
    Returns:
        str: Complete authorization URL
    """
    client_id = settings.GITHUB_CLIENT_ID
    scope = "read:user user:email"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    if state:
        params["state"] = state

    from urllib.parse import urlencode
    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_github_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """
    Exchange GitHub authorization code for access token.
    
    Args:
        code: Authorization code from GitHub
        redirect_uri: Must match the redirect_uri used in authorization
    
    Returns:
        dict: Token response containing access_token
    """
    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    headers = {"Accept": "application/json"}
    resp = requests.post(GITHUB_TOKEN_URL, data=data, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_github_userinfo(access_token: str) -> dict:
    """
    Fetch user information from GitHub API.
    
    Args:
        access_token: GitHub access token
    
    Returns:
        dict: User information including login, name, email, avatar_url
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.get(GITHUB_USERINFO_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    user_data = resp.json()
    
    # GitHub doesn't always return email in user endpoint, fetch separately if needed
    if not user_data.get("email"):
        email_resp = requests.get(
            "https://api.github.com/user/emails",
            headers=headers,
            timeout=10
        )
        if email_resp.status_code == 200:
            emails = email_resp.json()
            # Find primary email or first verified email
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    user_data["email"] = email_obj.get("email")
                    break
            if not user_data.get("email") and emails:
                # Fallback to first verified email
                for email_obj in emails:
                    if email_obj.get("verified"):
                        user_data["email"] = email_obj.get("email")
                        break
    
    return user_data
