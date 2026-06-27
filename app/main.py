# app/main.py

from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import resume, jobs, match    # ← add match

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Resume to Job Matching Agent",
    version="1.0.0"
)

app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(match.router)                  # ← add this


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}