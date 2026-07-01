# app/models/cover_letter.py

from pydantic import BaseModel
from typing import Optional, List


class CoverLetterRequest(BaseModel):
    """
    What the user sends to generate a cover letter.
    Combines candidate info + target job details.
    """
    # Candidate info
    full_name: str
    skills: List[str]
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    key_project: Optional[str] = None        # ← NEW: concrete project to reference

    # Target job info
    job_title: str
    company: str
    job_description: str

    # Optional tone customization
    tone: Optional[str] = "professional"

class CoverLetterResponse(BaseModel):
    """
    What we return after generating the cover letter.
    """
    success: bool
    message: str
    cover_letter: Optional[str] = None
    word_count: Optional[int] = None