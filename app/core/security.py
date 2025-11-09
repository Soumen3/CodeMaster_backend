"""
Security utilities for JWT token handling and authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from ..database.connection import get_db
from ..database.models import User

from icecream import ic

ic.disable()

# HTTP Bearer token scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Convert 'sub' to string if it's an integer (JWT spec requires string)
    if 'sub' in to_encode and isinstance(to_encode['sub'], int):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    ic("\n" + "="*60)
    ic("🔑 TOKEN CREATION DEBUG")
    ic("="*60)
    ic(f"Input data: {data}")
    ic(f"Encoded data (with sub as string): {to_encode}")
    ic(f"Expires in: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    ic(f"Expiry time: {expire}")
    ic(f"Token created: {encoded_jwt[:30]}...")
    ic(f"Token length: {len(encoded_jwt)}")
    ic("="*60 + "\n")
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        ic(f"🔍 Attempting to decode token...")
        ic(f"   Using SECRET_KEY: {settings.SECRET_KEY[:10]}...{settings.SECRET_KEY[-10:]}")
        ic(f"   Using ALGORITHM: {settings.ALGORITHM}")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        ic(f"✅ Token decoded successfully!")
        return payload
    except JWTError as e:
        ic(f"❌ JWTError: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session
        
    Returns:
        User object of the authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    ic("\n" + "="*60)
    ic("🔐 AUTHENTICATION DEBUG")
    ic("="*60)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        ic(f"✅ Token received: {token[:30]}...")
        ic(f"   Token length: {len(token)}")
        
        # Decode token
        payload = decode_access_token(token)
        ic(f"✅ Token decoded successfully")
        ic(f"   Payload: {payload}")
        
        # Extract user_id from token payload (it's stored as string in JWT)
        user_id_str = payload.get("sub")
        ic(f"   User ID from token (string): {user_id_str}")
        
        if user_id_str is None:
            ic("❌ ERROR: No 'sub' field in token payload")
            raise credentials_exception
        
        # Convert to integer for database query
        try:
            user_id = int(user_id_str)
            ic(f"   User ID converted to int: {user_id}")
        except (ValueError, TypeError):
            ic(f"❌ ERROR: Invalid user_id format: {user_id_str}")
            raise credentials_exception
            
    except HTTPException as e:
        ic(f"❌ HTTPException during token validation: {e.detail}")
        raise
    except Exception as e:
        ic(f"❌ Exception during token processing: {type(e).__name__}: {str(e)}")
        raise credentials_exception
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        ic(f"❌ ERROR: User with id {user_id} not found in database")
        raise credentials_exception
    
    ic(f"✅ User authenticated: {user.email} (id: {user.id})")
    ic("="*60 + "\n")
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user if token is provided, otherwise return None.
    Use this for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
