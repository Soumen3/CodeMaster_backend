import time
from sqlalchemy.orm import Session
from ..database.models import Problem, TestCase, Solution, SubmissionStatus
from ..database.schemas import SolutionCreate, SolutionResponse
from .compile_problem_service import execute_python, execute_javascript, execute_cpp, execute_java, execute_c, compare_outputs


def submit_problem_code(
    problem_id: int,
    code: str,
    language: str,
    user_id: int,
    db: Session
) -> dict:
    """
    Submit code for a problem and run against all test cases (including hidden ones).
    Saves the submission to the database.
    
    Args:
        problem_id: ID of the problem
        code: User's code
        language: Programming language
        user_id: ID of the user submitting
        db: Database session
        
    Returns:
        Dictionary with submission results and solution ID
    """
    # Fetch the problem
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise ValueError(f"Problem with id {problem_id} not found")
    
    # Fetch ALL test cases (including hidden ones)
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id
    ).all()
    
    if not test_cases:
        raise ValueError(f"No test cases found for problem {problem_id}")
    
    # Select execution function based on language
    execution_functions = {
        "python": execute_python,
        "javascript": execute_javascript,
        "cpp": execute_cpp,
        "java": execute_java,
        "c": execute_c
    }
    
    execute_func = execution_functions.get(language.lower())
    if not execute_func:
        raise ValueError(f"Unsupported language: {language}")
    
    # Run code against all test cases
    test_results = []
    passed_count = 0
    total_execution_time = 0
    submission_status = SubmissionStatus.ACCEPTED
    
    for test_case in test_cases:
        start_time = time.time()
        
        try:
            # Execute the code
            output, error = execute_func(code, test_case.input_data)
            execution_time = time.time() - start_time
            total_execution_time += execution_time
            
            if error:
                # Runtime or compilation error
                if "timed out" in error.lower():
                    submission_status = SubmissionStatus.TIME_LIMIT_EXCEEDED
                elif "compilation" in error.lower() or "syntax" in error.lower():
                    submission_status = SubmissionStatus.COMPILATION_ERROR
                else:
                    submission_status = SubmissionStatus.RUNTIME_ERROR
                
                test_results.append({
                    "test_case_id": test_case.id,
                    "input": test_case.input_data,
                    "expected_output": test_case.expected_output,
                    "actual_output": None,
                    "passed": False,
                    "error": error,
                    "execution_time": execution_time,
                    "is_hidden": test_case.is_hidden
                })
                break  # Stop on first error
            
            # Compare outputs
            passed = compare_outputs(output, test_case.expected_output)
            
            if passed:
                passed_count += 1
            else:
                submission_status = SubmissionStatus.WRONG_ANSWER
            
            test_results.append({
                "test_case_id": test_case.id,
                "input": test_case.input_data,
                "expected_output": test_case.expected_output,
                "actual_output": output,
                "passed": passed,
                "error": None,
                "execution_time": execution_time,
                "is_hidden": test_case.is_hidden
            })
            
            # Stop on first failure for wrong answer
            if not passed:
                break
                
        except Exception as e:
            execution_time = time.time() - start_time
            total_execution_time += execution_time
            submission_status = SubmissionStatus.RUNTIME_ERROR
            
            test_results.append({
                "test_case_id": test_case.id,
                "input": test_case.input_data,
                "expected_output": test_case.expected_output,
                "actual_output": None,
                "passed": False,
                "error": str(e),
                "execution_time": execution_time,
                "is_hidden": test_case.is_hidden
            })
            break
    
    # Create solution record in database
    solution_data = SolutionCreate(
        problem_id=problem_id,
        user_id=user_id,
        code=code,
        language=language,
        status=submission_status
    )
    
    solution = Solution(
        problem_id=solution_data.problem_id,
        user_id=solution_data.user_id,
        code=solution_data.code,
        language=solution_data.language,
        status=solution_data.status
    )
    
    db.add(solution)
    db.commit()
    db.refresh(solution)
    
    # Prepare response
    return {
        "solution_id": solution.id,
        "success": submission_status == SubmissionStatus.ACCEPTED,
        "status": submission_status.value,
        "message": _get_status_message(submission_status, passed_count, len(test_cases)),
        "test_results": test_results,
        "total_tests": len(test_cases),
        "passed_tests": passed_count,
        "execution_time": total_execution_time
    }


def _get_status_message(status: SubmissionStatus, passed: int, total: int) -> str:
    """Get a human-readable message based on submission status"""
    messages = {
        SubmissionStatus.ACCEPTED: f"Accepted! All {total} test cases passed.",
        SubmissionStatus.WRONG_ANSWER: f"Wrong Answer. Passed {passed}/{total} test cases.",
        SubmissionStatus.TIME_LIMIT_EXCEEDED: "Time Limit Exceeded.",
        SubmissionStatus.RUNTIME_ERROR: "Runtime Error.",
        SubmissionStatus.COMPILATION_ERROR: "Compilation Error."
    }
    return messages.get(status, "Unknown status")


def get_user_submissions(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> list:
    """
    Get all submissions for a user.
    
    Args:
        user_id: User ID
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of solutions
    """
    solutions = db.query(Solution).filter(
        Solution.user_id == user_id
    ).order_by(Solution.created_at.desc()).offset(skip).limit(limit).all()
    
    return solutions


def get_problem_submissions(
    user_id: int,
    problem_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list:
    """
    Get all submissions for a specific problem by a user.
    
    Args:
        user_id: User ID
        problem_id: Problem ID
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of solutions
    """
    solutions = db.query(Solution).filter(
        Solution.user_id == user_id,
        Solution.problem_id == problem_id
    ).order_by(Solution.created_at.desc()).offset(skip).limit(limit).all()
    
    return solutions


def get_submission_by_id(solution_id: int, db: Session):
    """
    Get a specific submission by ID.
    
    Args:
        solution_id: Solution ID
        db: Database session
        
    Returns:
        Solution object or None
    """
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise ValueError(f"Solution with id {solution_id} not found")
    return solution
