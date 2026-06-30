# app/models/resume.py

from pydantic import BaseModel
from typing import Optional, List


class UploadResponse(BaseModel):
    """Returned after successful file upload."""
    success: bool
    message: str
    filename: str
    file_size_kb: float
    file_type: str
    upload_path: Optional[str] = None


class ErrorResponse(BaseModel):
    """Consistent error shape."""
    success: bool = False
    error: str
    detail: Optional[str] = None


class WorkExperience(BaseModel):
    """One job/role from the candidate's history."""
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    """One educational qualification."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    year: Optional[str] = None


class ParsedResume(BaseModel):
    """
    Complete structured resume extracted by AI.
    This is the core data object passed through the system.
    """
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[WorkExperience] = []
    education: List[Education] = []
    raw_text: Optional[str] = None


class ParseResponse(BaseModel):
    """Returned to user after parsing is complete."""
    success: bool
    message: str
    parsed_resume: Optional[ParsedResume] = None