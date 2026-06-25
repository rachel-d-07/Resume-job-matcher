# app/main.py

from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import resume, jobs      # ← add jobs

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Resume to Job Matching Agent",
    version="1.0.0"
)

# ── Register routers ───────────────────────────────────────
app.include_router(resume.router)
app.include_router(jobs.router)             # ← add this


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}