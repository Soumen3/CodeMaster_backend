"""
Problem service for handling problem and test case operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..database.models import Problem, TestCase, Difficulty
from ..database.schemas import ProblemCreate, ProblemUpdate, TestCaseCreate, TestCaseUpdate


def get_problem_by_id(db: Session, problem_id: int) -> Problem:
    """
    Get a problem by ID or raise 404.
    
    Args:
        db: Database session
        problem_id: Problem ID
    
    Returns:
        Problem: The problem object
    
    Raises:
        HTTPException: If problem not found
    """
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id {problem_id} not found"
        )
    return problem


def get_problems_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[Difficulty] = None
) -> List[Problem]:
    """
    Get list of problems with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records
        difficulty: Optional difficulty filter
    
    Returns:
        List[Problem]: List of problems
    """
    query = db.query(Problem)
    
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    
    return query.offset(skip).limit(limit).all()


def create_problem(db: Session, problem_data: ProblemCreate) -> Problem:
    """
    Create a new problem.
    
    Args:
        db: Database session
        problem_data: Problem creation data
    
    Returns:
        Problem: Created problem
    
    Raises:
        HTTPException: If creation fails
    """
    try:
        db_problem = Problem(**problem_data.model_dump())
        db.add(db_problem)
        db.commit()
        db.refresh(db_problem)
        return db_problem
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create problem: {str(e)}"
        )


def update_problem(
    db: Session,
    problem_id: int,
    problem_update: ProblemUpdate
) -> Problem:
    """
    Update a problem.
    
    Args:
        db: Database session
        problem_id: Problem ID
        problem_update: Fields to update
    
    Returns:
        Problem: Updated problem
    
    Raises:
        HTTPException: If problem not found or update fails
    """
    db_problem = get_problem_by_id(db, problem_id)
    
    try:
        update_data = problem_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_problem, field, value)
        
        db.commit()
        db.refresh(db_problem)
        return db_problem
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update problem: {str(e)}"
        )


def delete_problem(db: Session, problem_id: int) -> None:
    """
    Delete a problem and all its test cases.
    
    Args:
        db: Database session
        problem_id: Problem ID
    
    Raises:
        HTTPException: If problem not found or deletion fails
    """
    db_problem = get_problem_by_id(db, problem_id)
    
    try:
        db.delete(db_problem)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete problem: {str(e)}"
        )


# ============= Test Case Service Functions =============

def get_test_case_by_id(db: Session, testcase_id: int) -> TestCase:
    """
    Get a test case by ID or raise 404.
    
    Args:
        db: Database session
        testcase_id: Test case ID
    
    Returns:
        TestCase: The test case object
    
    Raises:
        HTTPException: If test case not found
    """
    test_case = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {testcase_id} not found"
        )
    return test_case


def get_test_cases_for_problem(
    db: Session,
    problem_id: int,
    include_hidden: bool = False
) -> List[TestCase]:
    """
    Get all test cases for a problem.
    
    Args:
        db: Database session
        problem_id: Problem ID
        include_hidden: Whether to include hidden test cases
    
    Returns:
        List[TestCase]: List of test cases
    
    Raises:
        HTTPException: If problem not found
    """
    # Verify problem exists
    get_problem_by_id(db, problem_id)
    
    query = db.query(TestCase).filter(TestCase.problem_id == problem_id)
    
    if not include_hidden:
        query = query.filter(TestCase.is_hidden == False)
    
    return query.all()


def create_test_case(
    db: Session,
    problem_id: int,
    test_case_data: TestCaseCreate
) -> TestCase:
    """
    Create a new test case for a problem.
    
    Args:
        db: Database session
        problem_id: Problem ID
        test_case_data: Test case creation data
    
    Returns:
        TestCase: Created test case
    
    Raises:
        HTTPException: If problem not found or creation fails
    """
    # Verify problem exists
    get_problem_by_id(db, problem_id)
    
    # Ensure problem_id matches
    if test_case_data.problem_id != problem_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test case problem_id must match URL problem_id"
        )
    
    try:
        db_test_case = TestCase(**test_case_data.model_dump())
        db.add(db_test_case)
        db.commit()
        db.refresh(db_test_case)
        return db_test_case
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test case: {str(e)}"
        )


def update_test_case(
    db: Session,
    testcase_id: int,
    test_case_update: TestCaseUpdate
) -> TestCase:
    """
    Update a test case.
    
    Args:
        db: Database session
        testcase_id: Test case ID
        test_case_update: Fields to update
    
    Returns:
        TestCase: Updated test case
    
    Raises:
        HTTPException: If test case not found or update fails
    """
    db_test_case = get_test_case_by_id(db, testcase_id)
    
    try:
        update_data = test_case_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_test_case, field, value)
        
        db.commit()
        db.refresh(db_test_case)
        return db_test_case
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test case: {str(e)}"
        )


def delete_test_case(db: Session, testcase_id: int) -> None:
    """
    Delete a test case.
    
    Args:
        db: Database session
        testcase_id: Test case ID
    
    Raises:
        HTTPException: If test case not found or deletion fails
    """
    db_test_case = get_test_case_by_id(db, testcase_id)
    
    try:
        db.delete(db_test_case)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete test case: {str(e)}"
        )
