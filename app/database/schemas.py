from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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


# ============= TestCase Schemas =============

class TestCaseBase(BaseModel):
    """Base schema for test cases"""
    input_data: str
    expected_output: str
    explanation: Optional[str] = None
    is_hidden: bool = False


class TestCaseCreate(TestCaseBase):
    """Schema for creating a new test case"""
    problem_id: int


class TestCaseUpdate(BaseModel):
    """Schema for updating test case fields"""
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    explanation: Optional[str] = None
    is_hidden: Optional[bool] = None


class TestCaseResponse(TestCaseBase):
    """Schema for test case response"""
    id: int
    problem_id: int

    class Config:
        from_attributes = True


# ============= Constraint Schemas =============

class ConstraintBase(BaseModel):
    """Base schema for constraints"""
    description: str
    order: int = 0


class ConstraintCreate(ConstraintBase):
    """Schema for creating a new constraint"""
    problem_id: int


class ConstraintUpdate(BaseModel):
    """Schema for updating constraint fields"""
    description: Optional[str] = None
    order: Optional[int] = None


class ConstraintResponse(ConstraintBase):
    """Schema for constraint response"""
    id: int
    problem_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Problem Schemas =============

class ProblemBase(BaseModel):
    """Base schema for problems"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    difficulty: Difficulty


class ProblemCreate(ProblemBase):
    """Schema for creating a new problem"""
    pass


class ProblemUpdate(BaseModel):
    """Schema for updating problem fields"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty: Optional[Difficulty] = None


class ProblemResponse(ProblemBase):
    """Schema for problem response (includes id, timestamps, and optionally test cases)"""
    id: int
    created_at: datetime
    updated_at: datetime
    test_cases: Optional[List[TestCaseResponse]] = None
    constraints: Optional[List[ConstraintResponse]] = None

    class Config:
        from_attributes = True


class ProblemListResponse(BaseModel):
    """Schema for problem list item (without full description and test cases)"""
    id: int
    title: str
    difficulty: Difficulty
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Tag Schemas =============

class TagBase(BaseModel):
    """Base schema for tags"""
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """Schema for creating a new tag"""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int

    class Config:
        from_attributes = True


# ============= ProblemTag Schemas =============

class ProblemTagCreate(BaseModel):
    """Schema for adding a tag to a problem"""
    problem_id: int
    tag_id: int


class ProblemTagResponse(BaseModel):
    """Schema for problem-tag relationship response"""
    problem_id: int
    tag_id: int

    class Config:
        from_attributes = True
