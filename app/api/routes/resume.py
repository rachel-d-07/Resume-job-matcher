# app/api/routes/resume.py

import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.resume import UploadResponse, ErrorResponse
from app.core.config import settings

# APIRouter groups related endpoints together
router = APIRouter(
    prefix="/resume",        # all routes here start with /resume
    tags=["Resume Upload"]   # groups them in API docs
)

# Allowed file types
ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.document": ".docx"
}


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload a resume PDF or DOCX file"
)
async def upload_resume(
    file: UploadFile = File(..., description="PDF or DOCX resume file")
):
    """
    Accepts a resume file upload.
    Validates type and size.
    Saves to temporary upload directory.
    Returns upload confirmation.
    """

    # ── 1. Validate file type ──────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. "
                   f"Only PDF and DOCX are allowed."
        )

    # ── 2. Read file content ───────────────────────────────────
    content = await file.read()

    # ── 3. Validate file size ──────────────────────────────────
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is "
                   f"{settings.MAX_FILE_SIZE_MB}MB."
        )

    # ── 4. Reject empty files ──────────────────────────────────
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # ── 5. Create upload directory if it doesn't exist ────────
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # ── 6. Build safe file path ────────────────────────────────
    extension = ALLOWED_TYPES[file.content_type]
    safe_filename = Path(file.filename).stem  # strips directory traversal
    save_path = upload_dir / f"{safe_filename}{extension}"

    # ── 7. Save file to disk ───────────────────────────────────
    with open(save_path, "wb") as f:
        f.write(content)

    # ── 8. Return structured response ─────────────────────────
    return UploadResponse(
        success=True,
        message="Resume uploaded successfully.",
        filename=file.filename,
        file_size_kb=round(len(content) / 1024, 2),
        file_type=file.content_type,
        upload_path=str(save_path)
    )