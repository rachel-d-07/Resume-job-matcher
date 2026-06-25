# app/api/routes/jobs.py

from fastapi import APIRouter, HTTPException
from app.models.job import JobSearchRequest, JobSearchResponse
from app.services.job_searcher import job_searcher

router = APIRouter(
    prefix="/jobs",
    tags=["Job Search"]
)


@router.post(
    "/search",
    response_model=JobSearchResponse,
    summary="Search real job listings based on skills"
)
async def search_jobs(request: JobSearchRequest):
    """
    Accepts a list of skills from parsed resume.
    Returns real job listings from Adzuna.
    """

    # Validate skills list is not empty
    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="Skills list cannot be empty. "
                   "Parse your resume first."
        )

    # Call job search service
    result = job_searcher.search_jobs(
        skills=request.skills,
        location=request.location,
        country=request.country,
        page=request.page,
        results_per_page=request.results_per_page
    )

    return result