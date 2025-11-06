from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..database.models import Tag, ProblemTag, Problem
from ..database.schemas import (
    TagCreate,
    TagUpdate,
    TagResponse,
    ProblemTagCreate,
    ProblemTagResponse,
    ProblemResponse
)

router = APIRouter(
    tags=["tags"],
    prefix="/tags",
)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tag.
    
    Args:
        tag: Tag data (name)
        db: Database session
    
    Returns:
        TagResponse: Created tag with id
    """
    # Check if tag with same name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag.name}' already exists"
        )
    
    try:
        db_tag = Tag(**tag.model_dump())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tag: {str(e)}"
        )


@router.get("", response_model=List[TagResponse])
async def get_tags(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get list of all tags.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List[TagResponse]: List of tags
    """
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by ID.
    
    Args:
        tag_id: Tag ID
        db: Database session
    
    Returns:
        TagResponse: Tag details
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a tag.
    
    Args:
        tag_id: Tag ID
        tag_update: Fields to update
        db: Database session
    
    Returns:
        TagResponse: Updated tag
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    
    # Check if new name already exists
    if tag_update.name:
        existing_tag = db.query(Tag).filter(
            Tag.name == tag_update.name,
            Tag.id != tag_id
        ).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_update.name}' already exists"
            )
    
    try:
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)
        
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tag: {str(e)}"
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a tag and all its associations.
    
    Args:
        tag_id: Tag ID
        db: Database session
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    
    try:
        db.delete(db_tag)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tag: {str(e)}"
        )


# ============= Problem-Tag Association Routes =============

@router.post("/assign", response_model=ProblemTagResponse, status_code=status.HTTP_201_CREATED)
async def assign_tag_to_problem(
    problem_tag: ProblemTagCreate,
    db: Session = Depends(get_db)
):
    """
    Assign a tag to a problem.
    
    Args:
        problem_tag: Problem-tag association data
        db: Database session
    
    Returns:
        ProblemTagResponse: Created association
    """
    # Verify problem exists
    problem = db.query(Problem).filter(Problem.id == problem_tag.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id {problem_tag.problem_id} not found"
        )
    
    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == problem_tag.tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {problem_tag.tag_id} not found"
        )
    
    # Check if association already exists
    existing = db.query(ProblemTag).filter(
        ProblemTag.problem_id == problem_tag.problem_id,
        ProblemTag.tag_id == problem_tag.tag_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag is already assigned to this problem"
        )
    
    try:
        db_problem_tag = ProblemTag(**problem_tag.model_dump())
        db.add(db_problem_tag)
        db.commit()
        db.refresh(db_problem_tag)
        return db_problem_tag
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign tag: {str(e)}"
        )


@router.delete("/assign", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_problem(
    problem_id: int = Query(..., gt=0, description="Problem ID"),
    tag_id: int = Query(..., gt=0, description="Tag ID"),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a problem.
    
    Args:
        problem_id: Problem ID
        tag_id: Tag ID
        db: Database session
    """
    problem_tag = db.query(ProblemTag).filter(
        ProblemTag.problem_id == problem_id,
        ProblemTag.tag_id == tag_id
    ).first()
    
    if not problem_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Association not found"
        )
    
    try:
        db.delete(problem_tag)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove tag: {str(e)}"
        )


@router.get("/problem/{problem_id}", response_model=List[TagResponse])
async def get_tags_for_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all tags assigned to a specific problem.
    
    Args:
        problem_id: Problem ID
        db: Database session
    
    Returns:
        List[TagResponse]: List of tags
    """
    # Verify problem exists
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id {problem_id} not found"
        )
    
    # Get tags for this problem
    tags = db.query(Tag).join(ProblemTag).filter(
        ProblemTag.problem_id == problem_id
    ).all()
    
    return tags


@router.get("/tag/{tag_id}/problems", response_model=List[ProblemResponse])
async def get_problems_for_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all problems that have a specific tag.
    
    Args:
        tag_id: Tag ID
        db: Database session
    
    Returns:
        List[ProblemResponse]: List of problems
    """
    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    
    # Get problems for this tag
    problems = db.query(Problem).join(ProblemTag).filter(
        ProblemTag.tag_id == tag_id
    ).all()
    
    return problems
