from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"


class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    provider: OAuthProvider
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user
    
    Inherits from UserBase:
    - name: Optional[str] - User's display name
    - email: EmailStr - User's email (required, validated)
    - provider: OAuthProvider - OAuth provider (google/github, required)
    - avatar_url: Optional[str] - User's profile picture URL
    """
    pass


class UserUpdate(BaseModel):
    """Schema for updating user fields"""
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response (includes id and created_at)"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserLogin(BaseModel):
    """Schema for login response"""
    user: UserResponse
    access_token: Optional[str] = None
    token_type: str = "bearer"
