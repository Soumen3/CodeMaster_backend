from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..database.connection import get_db
from ..database.schemas import (
    SolutionResponse,
    SolutionListResponse,
    CompileProblemRequest,
    SubmitProblemResponse
)
from ..services.submission_service import (
    submit_problem_code,
    get_user_submissions,
    get_problem_submissions,
    get_submission_by_id
)
from ..core.security import get_current_user
from ..database.models import User

router = APIRouter(
    tags=["submissions"],
    prefix="/submissions",
)


@router.post("/submit", response_model=SubmitProblemResponse, status_code=status.HTTP_201_CREATED)
async def submit_code(
    submission_request: CompileProblemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit code for a problem. Runs against all test cases (including hidden ones).
    Saves the submission to the database.
    
    Args:
        submission_request: Contains problem_id, code, and language
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Submission results with solution ID
    """
    try:
        result = submit_problem_code(
            problem_id=submission_request.problem_id,
            code=submission_request.code,
            language=submission_request.language,
            user_id=current_user.id,
            db=db
        )
        return SubmitProblemResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=List[SolutionListResponse])
async def get_my_submissions(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all submissions for the current user.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        List of user's submissions
    """
    try:
        submissions = get_user_submissions(current_user.id, db, skip, limit)
        return submissions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/problem/{problem_id}", response_model=List[SolutionListResponse])
async def get_my_problem_submissions(
    problem_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all submissions for a specific problem by the current user.
    
    Args:
        problem_id: Problem ID
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        List of submissions for the problem
    """
    try:
        submissions = get_problem_submissions(current_user.id, problem_id, db, skip, limit)
        return submissions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{solution_id}", response_model=SolutionResponse)
async def get_submission(
    solution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific submission by ID.
    Only returns submissions belonging to the current user.
    
    Args:
        solution_id: Solution ID
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Solution details
    """
    try:
        submission = get_submission_by_id(solution_id, db)
        
        # Ensure the submission belongs to the current user
        if submission.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this submission"
            )
        
        return submission
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
