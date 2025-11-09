from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from ..database.connection import get_db
from ..core.security import get_current_user
from ..database.models import User, Solution, Problem, SubmissionStatus, Difficulty

router = APIRouter(
    tags=["users"],
    prefix="/users",
)


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for the current user.
    Similar to LeetCode profile stats.
    
    Returns:
        - Total problems solved (by difficulty)
        - Total submissions
        - Acceptance rate
        - Languages used
        - Recent submissions
        - Submission calendar/heatmap data
    """
    
    # Get total accepted solutions (unique problems)
    accepted_problems = db.query(
        func.count(distinct(Solution.problem_id))
    ).filter(
        Solution.user_id == current_user.id,
        Solution.status == SubmissionStatus.ACCEPTED
    ).scalar() or 0
    
    # Get accepted problems by difficulty
    difficulty_stats = {}
    for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        count = db.query(
            func.count(distinct(Solution.problem_id))
        ).join(
            Problem, Solution.problem_id == Problem.id
        ).filter(
            Solution.user_id == current_user.id,
            Solution.status == SubmissionStatus.ACCEPTED,
            Problem.difficulty == difficulty
        ).scalar() or 0
        
        difficulty_stats[difficulty.value] = count
    
    # Get total problems count by difficulty
    total_problems = {}
    for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        count = db.query(func.count(Problem.id)).filter(
            Problem.difficulty == difficulty
        ).scalar() or 0
        total_problems[difficulty.value] = count
    
    # Get total submissions
    total_submissions = db.query(func.count(Solution.id)).filter(
        Solution.user_id == current_user.id
    ).scalar() or 0
    
    # Get accepted submissions count
    accepted_submissions = db.query(func.count(Solution.id)).filter(
        Solution.user_id == current_user.id,
        Solution.status == SubmissionStatus.ACCEPTED
    ).scalar() or 0
    
    # Calculate acceptance rate
    acceptance_rate = round((accepted_submissions / total_submissions * 100), 2) if total_submissions > 0 else 0
    
    # Get language usage stats
    language_stats = db.query(
        Solution.language,
        func.count(Solution.id).label('count')
    ).filter(
        Solution.user_id == current_user.id,
        Solution.status == SubmissionStatus.ACCEPTED
    ).group_by(Solution.language).all()
    
    languages = {lang: count for lang, count in language_stats}
    
    # Get recent submissions (last 10)
    recent_submissions = db.query(Solution).filter(
        Solution.user_id == current_user.id
    ).order_by(Solution.created_at.desc()).limit(10).all()
    
    recent_activity = []
    for submission in recent_submissions:
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        recent_activity.append({
            "id": submission.id,
            "problem_id": submission.problem_id,
            "problem_title": problem.title if problem else "Unknown",
            "difficulty": problem.difficulty.value if problem else "unknown",
            "language": submission.language,
            "status": submission.status.value,
            "created_at": submission.created_at.isoformat()
        })
    
    # Get submission calendar data (last 12 months)
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    calendar_data = db.query(
        func.date(Solution.created_at).label('date'),
        func.count(Solution.id).label('count')
    ).filter(
        Solution.user_id == current_user.id,
        Solution.created_at >= start_date,
        Solution.status == SubmissionStatus.ACCEPTED
    ).group_by(func.date(Solution.created_at)).all()
    
    submission_calendar = {str(date): count for date, count in calendar_data}
    
    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
            "provider": current_user.provider.value,
            "created_at": current_user.created_at.isoformat()
        },
        "solved": {
            "total": accepted_problems,
            "easy": difficulty_stats.get("easy", 0),
            "medium": difficulty_stats.get("medium", 0),
            "hard": difficulty_stats.get("hard", 0),
        },
        "total_problems": {
            "easy": total_problems.get("easy", 0),
            "medium": total_problems.get("medium", 0),
            "hard": total_problems.get("hard", 0),
        },
        "submissions": {
            "total": total_submissions,
            "accepted": accepted_submissions,
            "acceptance_rate": acceptance_rate
        },
        "languages": languages,
        "recent_activity": recent_activity,
        "submission_calendar": submission_calendar
    }
