# app/models/analysis.py

from pydantic import BaseModel
from typing import List, Optional
from app.models.match import MatchedJob


class JobAnalysis(BaseModel):
    """
    AI-generated analysis for a single job match.
    This is what Gemini produces for each top job.
    """
    job_title: str
    company: str

    # Why this job fits the candidate
    match_explanation: str

    # Concrete strengths the candidate brings
    candidate_strengths: List[str] = []

    # Skills in the job the candidate lacks
    skill_gaps: List[str] = []

    # What to learn and in what order
    learning_priorities: List[str] = []

    # Honest assessment of application chances
    application_advice: str

    # Overall AI confidence in this match
    ai_match_rating: str          # "Strong", "Moderate", "Weak"


class SkillGapReport(BaseModel):
    """
    Overall skill gap report across ALL analyzed jobs.
    Shows patterns — skills missing across multiple jobs.
    """
    # Skills missing in 2+ jobs (high priority to learn)
    critical_gaps: List[str] = []

    # Skills missing in only 1 job
    minor_gaps: List[str] = []

    # Skills candidate has that appear in most jobs
    strongest_skills: List[str] = []

    # Overall market readiness assessment
    market_readiness: str

    # Top 3 things to do right now
    immediate_actions: List[str] = []


class AnalysisResponse(BaseModel):
    """
    Complete analysis report returned to the user.
    """
    success: bool
    message: str
    candidate_name: Optional[str] = None
    total_jobs_analyzed: int
    job_analyses: List[JobAnalysis] = []
    skill_gap_report: Optional[SkillGapReport] = None