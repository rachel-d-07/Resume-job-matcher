# app/models/resume.py

from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    """
    What we return to the user after a successful upload.
    """
    success: bool
    message: str
    filename: str
    file_size_kb: float
    file_type: str
    upload_path: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Consistent error shape returned on failures.
    """
    success: bool = False
    error: str
    detail: Optional[str] = None