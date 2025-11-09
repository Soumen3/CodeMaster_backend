from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..database.schemas import (
    ProblemCreate,
    ProblemUpdate,
    ProblemResponse,
    ProblemListResponse,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse
)
from ..services.problem_service import (
    get_problem_by_id,
    get_problems_list,
    create_problem as create_problem_service,
    update_problem as update_problem_service,
    delete_problem as delete_problem_service,
    get_test_cases_for_problem,
    create_test_case as create_test_case_service,
    update_test_case as update_test_case_service,
    delete_test_case as delete_test_case_service
)
from ..services.code_template_service import get_code_template, parse_parameters_from_json

router = APIRouter(
    tags=["problems"],
    prefix="/problems",
)


@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem: ProblemCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new problem.
    
    Args:
        problem: Problem data (title, description, difficulty)
        db: Database session
    
    Returns:
        ProblemResponse: Created problem with id and timestamps
    """
    return create_problem_service(db, problem)


@router.get("", response_model=List[ProblemListResponse])
async def get_problems(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    difficulty: str = Query(None, description="Filter by difficulty (easy/medium/hard)"),
    db: Session = Depends(get_db)
):
    """
    Get list of problems with optional filtering.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        difficulty: Filter by difficulty (easy/medium/hard)
        db: Database session
    
    Returns:
        List[ProblemListResponse]: List of problems (without full details)
    """
    return get_problems_list(db, skip, limit, difficulty)


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific problem by ID with its test cases.
    
    Args:
        problem_id: Problem ID
        db: Database session
    
    Returns:
        ProblemResponse: Problem details with test cases
    """
    return get_problem_by_id(db, problem_id)


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    problem_update: ProblemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a problem.
    
    Args:
        problem_id: Problem ID
        problem_update: Fields to update
        db: Database session
    
    Returns:
        ProblemResponse: Updated problem
    """
    return update_problem_service(db, problem_id, problem_update)


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a problem and all its test cases.
    
    Args:
        problem_id: Problem ID
        db: Database session
    """
    delete_problem_service(db, problem_id)


# ============= Test Case Routes =============

@router.post("/{problem_id}/testcases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    problem_id: int,
    test_case: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new test case for a problem.
    
    Args:
        problem_id: Problem ID
        test_case: Test case data
        db: Database session
    
    Returns:
        TestCaseResponse: Created test case
    """
    return create_test_case_service(db, problem_id, test_case)


@router.get("/{problem_id}/testcases", response_model=List[TestCaseResponse])
async def get_test_cases(
    problem_id: int,
    include_hidden: bool = Query(False, description="Whether to include hidden test cases"),
    db: Session = Depends(get_db)
):
    """
    Get all test cases for a problem.
    
    Args:
        problem_id: Problem ID
        include_hidden: Whether to include hidden test cases
        db: Database session
    
    Returns:
        List[TestCaseResponse]: List of test cases
    """
    return get_test_cases_for_problem(db, problem_id, include_hidden)


@router.put("/testcases/{testcase_id}", response_model=TestCaseResponse)
async def update_test_case(
    testcase_id: int,
    test_case_update: TestCaseUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a test case.
    
    Args:
        testcase_id: Test case ID
        test_case_update: Fields to update
        db: Database session
    
    Returns:
        TestCaseResponse: Updated test case
    """
    return update_test_case_service(db, testcase_id, test_case_update)


@router.delete("/testcases/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    testcase_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a test case.
    
    Args:
        testcase_id: Test case ID
        db: Database session
    """
    delete_test_case_service(db, testcase_id)


@router.get("/{problem_id}/template/{language}")
async def get_problem_template(
    problem_id: int,
    language: str,
    db: Session = Depends(get_db)
):
    """
    Get code template for a specific problem and language.
    
    Args:
        problem_id: Problem ID
        language: Programming language (python, javascript, cpp, java, c)
        db: Database session
    
    Returns:
        Code template string
    """
    from ..database.models import Problem
    
    # Fetch problem
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Parse parameters
    parameters = parse_parameters_from_json(problem.parameters)
    
    # Generate template
    try:
        template = get_code_template(
            language=language,
            function_name=problem.function_name or "solution",
            parameters=parameters,
            return_type=problem.return_type
        )
        
        return {"code": template}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
