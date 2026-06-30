# app/api/routes/analysis.py

from fastapi import APIRouter, HTTPException
from app.models.match import MatchRequest
from app.models.analysis import AnalysisResponse
from app.models.resume import ParsedResume
from app.services.job_searcher import job_searcher
from app.services.job_matcher import job_matcher
from app.services.ai_analyzer import ai_analyzer
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/analysis",
    tags=["AI Analysis"]
)


class FullAnalysisRequest(BaseModel):
    """
    All-in-one request:
    Skills + experience → search + match + AI explain
    """
    skills: List[str]
    experience_titles: List[str] = []
    full_name: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = "New York"
    country: Optional[str] = "us"
    results_per_page: Optional[int] = 10


@router.post(
    "/full",
    response_model=AnalysisResponse,
    summary="Complete pipeline: search + match + AI explain"
)
async def full_analysis(request: FullAnalysisRequest):
    """
    The flagship endpoint — does everything:
    1. Searches real jobs
    2. Scores and ranks them
    3. AI explains each top match
    4. Generates skill gap report
    5. Returns complete career analysis
    """

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="Skills list cannot be empty."
        )

    # ── Step 1: Search real jobs ───────────────────────────────
    search_result = job_searcher.search_jobs(
        skills=request.skills,
        location=request.location,
        country=request.country,
        page=1,
        results_per_page=request.results_per_page
    )

    if not search_result.jobs:
        raise HTTPException(
            status_code=404,
            detail="No jobs found. Try different skills or location."
        )

    # ── Step 2: Score and rank jobs ────────────────────────────
    ranked_jobs = job_matcher.match_and_rank(
        candidate_skills=request.skills,
        candidate_titles=request.experience_titles,
        candidate_location=request.location or "",
        jobs=search_result.jobs
    )

    # ── Step 3: Build resume object for AI ────────────────────
    resume = ParsedResume(
        full_name=request.full_name,
        skills=request.skills,
        experience=[],
        education=[],
        summary=request.summary
    )

    # ── Step 4: AI analyzes top matches ───────────────────────
    analysis = ai_analyzer.analyze(
        resume=resume,
        matched_jobs=ranked_jobs
    )

    return analysis