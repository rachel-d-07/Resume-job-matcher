# app/api/routes/match.py

from fastapi import APIRouter, HTTPException
from app.models.match import MatchRequest, MatchResponse
from app.services.job_searcher import job_searcher
from app.services.job_matcher import job_matcher

router = APIRouter(
    prefix="/match",
    tags=["Job Matching"]
)


@router.post(
    "/jobs",
    response_model=MatchResponse,
    summary="Search and rank jobs matching the candidate profile"
)
async def match_jobs(request: MatchRequest):
    """
    One endpoint that does it all:
    1. Searches real jobs based on skills
    2. Scores each job against candidate profile
    3. Returns ranked matches with scores
    """

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="Skills list cannot be empty."
        )

    # ── Step 1: Search real jobs ───────────────────────────────
    search_result = job_searcher.search_jobs(
        skills=request.skills,
        location=request.location or "New York",
        country=request.country or "us",
        page=1,
        results_per_page=request.results_per_page or 10
    )
    print(f"DEBUG jobs found: {search_result.total_found}")
    print(f"DEBUG skills: {request.skills}")
    print(f"DEBUG country: {request.country}")
    print(f"DEBUG location: {request.location}")
    if not search_result.jobs:
        return MatchResponse(
            success=False,
            message="No jobs found for your profile.",
            total_jobs_analyzed=0,
            matched_jobs=[]
        )

    # ── Step 2: Score and rank jobs ────────────────────────────
    ranked_jobs = job_matcher.match_and_rank(
        candidate_skills=request.skills,
        candidate_titles=request.experience_titles,
        candidate_location=request.location or "",
        jobs=search_result.jobs
    )

    return MatchResponse(
        success=True,
        message=f"Analyzed {len(ranked_jobs)} jobs. "
                f"Top match: {ranked_jobs[0].match_label if ranked_jobs else 'N/A'}",
        total_jobs_analyzed=len(ranked_jobs),
        matched_jobs=ranked_jobs
    )