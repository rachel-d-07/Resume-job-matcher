# app/services/skill_extractor.py

import json
from google import genai
from app.core.config import settings
from app.models.resume import ParsedResume, WorkExperience, Education


class SkillExtractor:
    """
    Uses Gemini AI to extract structured information from resume text.
    Responsibility: raw text → structured ParsedResume object.
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def extract(self, raw_text: str) -> ParsedResume:
        prompt = self._build_prompt(raw_text)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return self._parse_response(response.text, raw_text)

    def _build_prompt(self, resume_text: str) -> str:
        return f"""
You are an expert resume parser. Extract structured information from the resume text below.

Return ONLY a valid JSON object with this exact structure:
{{
    "full_name": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "summary": "brief professional summary or null",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
        {{
            "company": "string or null",
            "role": "string or null",
            "duration": "string or null",
            "description": "string or null"
        }}
    ],
    "education": [
        {{
            "institution": "string or null",
            "degree": "string or null",
            "field": "string or null",
            "year": "string or null"
        }}
    ]
}}

Rules:
- Return ONLY the JSON object. No explanation, no markdown, no code fences.
- If information is not found, use null for strings and [] for arrays.
- Extract ALL skills mentioned including tools, languages, frameworks, soft skills.
- Keep experience and education in chronological order (most recent first).

Resume Text:
---
{resume_text}
---
"""

    def _parse_response(
        self,
        ai_response: str,
        raw_text: str
    ) -> ParsedResume:
        try:
            cleaned = ai_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()

            data = json.loads(cleaned)

            experience_list = [
                WorkExperience(**exp)
                for exp in data.get("experience", [])
            ]

            education_list = [
                Education(**edu)
                for edu in data.get("education", [])
            ]

            return ParsedResume(
                full_name=data.get("full_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                location=data.get("location"),
                summary=data.get("summary"),
                skills=data.get("skills", []),
                experience=experience_list,
                education=education_list,
                raw_text=raw_text
            )

        except json.JSONDecodeError:
            return ParsedResume(
                raw_text=raw_text,
                skills=[],
                experience=[],
                education=[]
            )


skill_extractor = SkillExtractor()