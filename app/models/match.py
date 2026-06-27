# app/models/match.py

from pydantic import BaseModel
from typing import Optional, List
from app.models.job import Job


class MatchedJob(BaseModel):
    """
    A job with its match score and reasoning.
    Extends Job with matching metadata.
    """
    job: Job                              # the full job object
    match_score: float                    # 0.0 to 1.0
    match_percentage: int                 # 0 to 100 (human readable)
    matched_skills: List[str] = []        # skills that matched
    missing_skills: List[str] = []        # skills in job but not resume
    match_label: str = ""                 # "Excellent", "Good", "Fair"


class MatchRequest(BaseModel):
    """
    What the matching engine needs to do its job.
    """
    skills: List[str]                     # candidate skills
    experience_titles: List[str] = []     # candidate job titles
    location: Optional[str] = None        # candidate location
    country: Optional[str] = "us"
    results_per_page: Optional[int] = 10


class MatchResponse(BaseModel):
    """
    What we return after matching.
    """
    success: bool
    message: str
    total_jobs_analyzed: int
    matched_jobs: List[MatchedJob] = []