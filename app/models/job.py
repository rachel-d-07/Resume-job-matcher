# app/models/job.py

from pydantic import BaseModel
from typing import Optional, List


class Job(BaseModel):
    """
    Normalized job listing.
    Every job API response gets transformed into this shape.
    This decouples our system from any specific API.
    """
    id: str                              # unique job identifier
    title: str                           # job title
    company: str                         # company name
    location: str                        # job location
    description: str                     # full job description
    salary_min: Optional[float] = None   # minimum salary
    salary_max: Optional[float] = None   # maximum salary
    currency: Optional[str] = None       # salary currency
    job_url: str                         # direct application link
    posted_date: Optional[str] = None    # when job was posted
    contract_type: Optional[str] = None  # full-time, part-time, etc.
    category: Optional[str] = None       # job category/industry


class JobSearchRequest(BaseModel):
    """
    What the user sends when requesting a job search.
    """
    skills: List[str]                    # from parsed resume
    location: Optional[str] = "New York" # preferred location
    country: Optional[str] = "us"   
    page: Optional[int] = 1             # pagination
    results_per_page: Optional[int] = 10


class JobSearchResponse(BaseModel):
    """
    What we return after a job search.
    """
    success: bool
    message: str
    total_found: int
    page: int
    jobs: List[Job] = []