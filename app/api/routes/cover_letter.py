# app/api/routes/cover_letter.py

from fastapi import APIRouter, HTTPException
from app.models.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.cover_letter_generator import cover_letter_generator

router = APIRouter(
    prefix="/cover-letter",
    tags=["Cover Letter"]
)


@router.post(
    "/generate",
    response_model=CoverLetterResponse,
    summary="Generate a personalized cover letter for a specific job"
)
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Takes candidate info and target job details.
    Returns a ready-to-send, personalized cover letter.
    """

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="Skills list cannot be empty."
        )

    if not request.job_description:
        raise HTTPException(
            status_code=400,
            detail="Job description is required to personalize the letter."
        )

    result = cover_letter_generator.generate(request)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)

    return result