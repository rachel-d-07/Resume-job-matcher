# app/services/cover_letter_generator.py

from datetime import date
from google import genai
from app.core.config import settings
from app.models.cover_letter import CoverLetterRequest, CoverLetterResponse


class CoverLetterGenerator:
    """
    Uses Gemini AI to generate personalized cover letters.
    Assembles full letter with proper header, greeting, and structure.
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def generate(self, request: CoverLetterRequest) -> CoverLetterResponse:
        try:
            # Step 1: AI writes the body content only
            prompt = self._build_prompt(request)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            # Step 2: Our code assembles the full formatted letter
            full_letter = self._assemble_letter(request, response.text)
            word_count = len(full_letter.split())

            return CoverLetterResponse(
                success=True,
                message="Cover letter generated successfully.",
                cover_letter=full_letter,
                word_count=word_count
            )

        except Exception as e:
            return CoverLetterResponse(
                success=False,
                message=f"Cover letter generation failed: {str(e)}"
            )

    def _assemble_letter(
        self,
        request: CoverLetterRequest,
        ai_body: str
    ) -> str:
        """
        Assembles the full cover letter with:
        - Candidate header (name, title, education)
        - Date
        - Company address block
        - Greeting
        - AI-written body
        - Formal sign-off
        """
        today = date.today().strftime("%B %d, %Y")

        # Clean AI body first
        body = self._clean_letter(ai_body)

        letter = f"""{request.full_name}
{request.job_title} Candidate
{request.education_summary or 'AI & ML Student'}


{today}
{request.company}


Dear Hiring Manager,


{body}


Sincerely,
{request.full_name}"""

        return letter

    def _build_prompt(self, request: CoverLetterRequest) -> str:
        """
        Asks AI to write ONLY the body paragraphs.
        Header, greeting, and sign-off are handled by _assemble_letter.
        """
        skills_str = ", ".join(request.skills[:10])

        return f"""
You are an expert career writer. Write ONLY the body paragraphs of a
cover letter — no header, no date, no "Dear Hiring Manager", no sign-off.
Those are handled separately. Write ONLY 3-4 paragraphs of body content.

Use ONLY the facts provided below. Never invent experience or achievements.

=== CANDIDATE FACTS ===
Name: {request.full_name}
Skills: {skills_str}
Experience: {request.experience_summary or 'Recent graduate / student'}
Education: {request.education_summary or 'Not specified'}
Key Project: {request.key_project or 'Not specified'}

=== TARGET JOB ===
Position: {request.job_title}
Company: {request.company}
Job Description: {request.job_description[:1000]}

=== REQUIRED PARAGRAPH STRUCTURE ===

Paragraph 1 — Opening intent:
  Start with "I am excited to apply for the {request.job_title} role
  at {request.company}." Then add one sentence referencing a SPECIFIC
  technical requirement or responsibility from the job description.
  Do not use generic enthusiasm — name something concrete from the posting.

Paragraph 2 — Skill proof points:
  Write exactly this format for 2-3 skills:

  [Skill Name]
  ✔️ [One concrete proof point — what was built or done using this skill,
     drawn from Key Project or Experience. Connect it to the job requirement.]

  Example format (do not copy content, only format):
  Python
  ✔️ Used Python to build the complete backend pipeline for an AI agent,
     handling resume parsing, API integration, and ML scoring logic.

Paragraph 3 — Project deep-dive:
  Reference the Key Project by name. Explain specifically what was built,
  which technologies were used (FastAPI, Gemini AI, etc.), and draw a
  direct line to why this makes the candidate ready for THIS role.
  Be specific — avoid vague descriptions.

Paragraph 4 — Closing:
  Express genuine interest in the company tied to something specific in
  the job description (their focus on production-ready systems, their
  AI mission, etc.). One or two sentences maximum. Thank them for their
  time and consideration.

=== WRITING RULES ===
1. Tone: {request.tone} — confident, warm, professional.
2. Total body length: 220-300 words strictly.
3. Never use: "I believe I would be a great fit", "I am writing to
   express my interest", or any other generic filler phrase.
4. Never fabricate metrics, years of experience, or company names
   not provided in the facts above.
5. No markdown bold (**text**) — use plain text only.
6. No sign-off, no "Dear Hiring Manager" — body paragraphs only.

Write the body paragraphs now.
"""

    def _clean_letter(self, raw_text: str) -> str:
        """Removes markdown artifacts from AI response."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        # Remove any bold markdown that slips through
        cleaned = cleaned.replace("**", "")
        return cleaned.strip()


cover_letter_generator = CoverLetterGenerator()