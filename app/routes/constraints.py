from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..database.schemas import (
    ConstraintCreate,
    ConstraintUpdate,
    ConstraintResponse
)
from ..services.constraint_service import (
    create_constraint as create_constraint_service,
    get_constraints_for_problem,
    get_constraint_by_id,
    update_constraint as update_constraint_service,
    delete_constraint as delete_constraint_service
)

router = APIRouter(
    tags=["constraints"],
    prefix="/constraints",
)


@router.post("", response_model=ConstraintResponse, status_code=status.HTTP_201_CREATED)
async def create_constraint(
    constraint: ConstraintCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new constraint for a problem.
    
    Args:
        constraint: Constraint data (problem_id, description, order)
        db: Database session
    
    Returns:
        ConstraintResponse: Created constraint
    """
    return create_constraint_service(db, constraint)


@router.get("/problem/{problem_id}", response_model=List[ConstraintResponse])
async def get_constraints(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all constraints for a specific problem.
    
    Args:
        problem_id: Problem ID
        db: Database session
    
    Returns:
        List[ConstraintResponse]: List of constraints ordered by 'order' field
    """
    return get_constraints_for_problem(db, problem_id)


@router.get("/{constraint_id}", response_model=ConstraintResponse)
async def get_constraint(
    constraint_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific constraint by ID.
    
    Args:
        constraint_id: Constraint ID
        db: Database session
    
    Returns:
        ConstraintResponse: Constraint details
    """
    return get_constraint_by_id(db, constraint_id)


@router.put("/{constraint_id}", response_model=ConstraintResponse)
async def update_constraint(
    constraint_id: int,
    constraint_update: ConstraintUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a constraint.
    
    Args:
        constraint_id: Constraint ID
        constraint_update: Fields to update (description, order)
        db: Database session
    
    Returns:
        ConstraintResponse: Updated constraint
    """
    return update_constraint_service(db, constraint_id, constraint_update)


@router.delete("/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constraint(
    constraint_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a constraint.
    
    Args:
        constraint_id: Constraint ID
        db: Database session
    """
    delete_constraint_service(db, constraint_id)
