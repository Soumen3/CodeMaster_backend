from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from ..database.models import Constraint, Problem
from ..database.schemas import ConstraintCreate, ConstraintUpdate


def create_constraint(db: Session, constraint: ConstraintCreate) -> Constraint:
    """
    Create a new constraint for a problem.
    
    Args:
        db: Database session
        constraint: Constraint data (problem_id, description, order)
    
    Returns:
        Constraint: Created constraint
    
    Raises:
        HTTPException: If problem not found
    """
    # Check if problem exists
    problem = db.query(Problem).filter(Problem.id == constraint.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id {constraint.problem_id} not found"
        )
    
    db_constraint = Constraint(
        problem_id=constraint.problem_id,
        description=constraint.description,
        order=constraint.order
    )
    db.add(db_constraint)
    db.commit()
    db.refresh(db_constraint)
    return db_constraint


def get_constraints_for_problem(db: Session, problem_id: int) -> List[Constraint]:
    """
    Get all constraints for a specific problem, ordered by the 'order' field.
    
    Args:
        db: Database session
        problem_id: Problem ID
    
    Returns:
        List[Constraint]: List of constraints
    
    Raises:
        HTTPException: If problem not found
    """
    # Check if problem exists
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id {problem_id} not found"
        )
    
    constraints = db.query(Constraint)\
        .filter(Constraint.problem_id == problem_id)\
        .order_by(Constraint.order)\
        .all()
    
    return constraints


def get_constraint_by_id(db: Session, constraint_id: int) -> Constraint:
    """
    Get a specific constraint by ID.
    
    Args:
        db: Database session
        constraint_id: Constraint ID
    
    Returns:
        Constraint: Constraint object
    
    Raises:
        HTTPException: If constraint not found
    """
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constraint with id {constraint_id} not found"
        )
    return constraint


def update_constraint(db: Session, constraint_id: int, constraint_update: ConstraintUpdate) -> Constraint:
    """
    Update a constraint.
    
    Args:
        db: Database session
        constraint_id: Constraint ID
        constraint_update: Fields to update
    
    Returns:
        Constraint: Updated constraint
    
    Raises:
        HTTPException: If constraint not found
    """
    constraint = get_constraint_by_id(db, constraint_id)
    
    # Update only provided fields
    if constraint_update.description is not None:
        constraint.description = constraint_update.description
    if constraint_update.order is not None:
        constraint.order = constraint_update.order
    
    db.commit()
    db.refresh(constraint)
    return constraint


def delete_constraint(db: Session, constraint_id: int) -> None:
    """
    Delete a constraint.
    
    Args:
        db: Database session
        constraint_id: Constraint ID
    
    Raises:
        HTTPException: If constraint not found
    """
    constraint = get_constraint_by_id(db, constraint_id)
    db.delete(constraint)
    db.commit()
