from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.schemas import CompileProblemRequest, CompileProblemResponse
from ..services.compile_problem_service import compile_problem_code

router = APIRouter(
    tags=["compile_problem"],
    prefix="/compile_problem",
)

@router.post("", response_model=CompileProblemResponse, status_code=status.HTTP_200_OK)
async def compile_problem(
    compile_request: CompileProblemRequest,
    db: Session = Depends(get_db)
):
    print(compile_request)
    """
    Compile and run code for a given problem.
    
    Args:
        compile_request: CompileProblemRequest data (problem_id, code, language)
        db: Database session
    """
    try:
        result = compile_problem_code(compile_request, db)
        return CompileProblemResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
