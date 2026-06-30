# app/services/ai_analyzer.py

import json
from google import genai                          # ← new import
from google.genai import types                    # ← new import
from typing import List
from app.core.config import settings
from app.models.resume import ParsedResume
from app.models.match import MatchedJob
from app.models.analysis import JobAnalysis, SkillGapReport, AnalysisResponse


class AIAnalyzer:
    MAX_JOBS_TO_ANALYZE = 1

    def __init__(self):
        # ← new client setup
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def analyze(
        self,
        resume: ParsedResume,
        matched_jobs: List[MatchedJob]
    ) -> AnalysisResponse:

        top_jobs = matched_jobs[:self.MAX_JOBS_TO_ANALYZE]

        if not top_jobs:
            return AnalysisResponse(
                success=False,
                message="No jobs to analyze.",
                total_jobs_analyzed=0
            )

        job_analyses = []
        for matched_job in top_jobs:
            analysis = self._analyze_single_job(resume, matched_job)
            if analysis:
                job_analyses.append(analysis)

        skill_gap_report = self._generate_skill_gap_report(
            resume, job_analyses
        )

        return AnalysisResponse(
            success=True,
            message=f"AI analysis complete for top {len(job_analyses)} jobs.",
            candidate_name=resume.full_name,
            total_jobs_analyzed=len(job_analyses),
            job_analyses=job_analyses,
            skill_gap_report=skill_gap_report
        )

    def _analyze_single_job(
        self,
        resume: ParsedResume,
        matched_job: MatchedJob
    ) -> JobAnalysis | None:
        try:
            prompt = self._build_job_analysis_prompt(resume, matched_job)

            # ← new API call style
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return self._parse_job_analysis(
                response.text,
                matched_job.job.title,
                matched_job.job.company
            )
        except Exception as e:
            print(f"Analysis failed for {matched_job.job.title}: {e}")
            return None

    def _build_job_analysis_prompt(
        self,
        resume: ParsedResume,
        matched_job: MatchedJob
    ) -> str:

        skills_str = ", ".join(resume.skills[:20]) if resume.skills else "Not specified"

        experience_str = ""
        for exp in resume.experience[:3]:
            experience_str += f"- {exp.role} at {exp.company} ({exp.duration})\n"

        education_str = ""
        for edu in resume.education[:2]:
            education_str += f"- {edu.degree} in {edu.field} from {edu.institution}\n"

        job = matched_job.job
        description_preview = job.description[:800] if job.description else ""
        matched_skills_str = ", ".join(matched_job.matched_skills)
        missing_skills_str = ", ".join(matched_job.missing_skills)

        return f"""
You are a senior technical recruiter and career coach with 15 years of experience.
Analyze this candidate's fit for the job below and provide honest, specific, actionable insights.

=== CANDIDATE PROFILE ===
Name: {resume.full_name or 'Not provided'}
Skills: {skills_str}

Work Experience:
{experience_str or 'Not provided'}

Education:
{education_str or 'Not provided'}

Summary: {resume.summary or 'Not provided'}

=== JOB DETAILS ===
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description: {description_preview}

=== MATCHING DATA ===
Skills already matched: {matched_skills_str or 'None'}
Skills missing: {missing_skills_str or 'None'}
Current match score: {matched_job.match_percentage}%

=== YOUR TASK ===
Provide a structured analysis in this EXACT JSON format:
{{
    "match_explanation": "2-3 sentences explaining specifically why this job fits or doesn't fit this candidate. Be honest and specific.",
    "candidate_strengths": ["strength1", "strength2", "strength3"],
    "skill_gaps": ["gap1", "gap2", "gap3"],
    "learning_priorities": ["learn X first because...", "then learn Y because..."],
    "application_advice": "1-2 sentences of honest advice on whether to apply and how to position themselves.",
    "ai_match_rating": "Strong" or "Moderate" or "Weak"
}}

Rules:
- Return ONLY the JSON object. No markdown, no explanation outside JSON.
- Be specific — mention actual skills, actual job requirements.
- Be honest — do not inflate the match if it is weak.
- learning_priorities should be ordered (most important first).
- Keep each field concise but meaningful.
"""

    def _parse_job_analysis(
        self,
        ai_response: str,
        job_title: str,
        company: str
    ) -> JobAnalysis | None:
        try:
            cleaned = ai_response.strip()
            if "```" in cleaned:
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()

            data = json.loads(cleaned)

            return JobAnalysis(
                job_title=job_title,
                company=company,
                match_explanation=data.get("match_explanation", ""),
                candidate_strengths=data.get("candidate_strengths", []),
                skill_gaps=data.get("skill_gaps", []),
                learning_priorities=data.get("learning_priorities", []),
                application_advice=data.get("application_advice", ""),
                ai_match_rating=data.get("ai_match_rating", "Moderate")
            )

        except json.JSONDecodeError as e:
            print(f"JSON parse failed for {job_title}: {e}")
            return None

    def _generate_skill_gap_report(
        self,
        resume: ParsedResume,
        job_analyses: List[JobAnalysis]
    ) -> SkillGapReport:
        try:
            all_gaps = []
            for analysis in job_analyses:
                all_gaps.extend(analysis.skill_gaps)

            gap_frequency = {}
            for gap in all_gaps:
                gap_lower = gap.lower()
                gap_frequency[gap_lower] = gap_frequency.get(gap_lower, 0) + 1

            critical = [g for g, c in gap_frequency.items() if c >= 2]
            minor = [g for g, c in gap_frequency.items() if c == 1]

            all_strengths = []
            for analysis in job_analyses:
                all_strengths.extend(analysis.candidate_strengths)

            strength_frequency = {}
            for strength in all_strengths:
                s_lower = strength.lower()
                strength_frequency[s_lower] = strength_frequency.get(s_lower, 0) + 1

            top_strengths = sorted(
                strength_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            strongest = [s[0] for s in top_strengths]

            prompt = self._build_gap_report_prompt(resume, critical, minor, strongest)

            # ← new API call style
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            summary_data = self._parse_gap_report(response.text)

            return SkillGapReport(
                critical_gaps=critical[:5],
                minor_gaps=minor[:5],
                strongest_skills=strongest,
                market_readiness=summary_data.get(
                    "market_readiness",
                    "Moderate — building core skills"
                ),
                immediate_actions=summary_data.get("immediate_actions", [])
            )

        except Exception as e:
            print(f"Skill gap report failed: {e}")
            return SkillGapReport(market_readiness="Analysis unavailable")

    def _build_gap_report_prompt(
        self,
        resume: ParsedResume,
        critical_gaps: List[str],
        minor_gaps: List[str],
        strengths: List[str]
    ) -> str:

        skills_str = ", ".join(resume.skills[:15])

        return f"""
You are a senior AI/ML career coach.
Based on this candidate's job search analysis, provide a career readiness summary.

Candidate Skills: {skills_str}
Critical Skill Gaps (missing in multiple jobs): {", ".join(critical_gaps)}
Minor Gaps (missing in one job): {", ".join(minor_gaps)}
Candidate Strengths (appearing across jobs): {", ".join(strengths)}

Return ONLY this JSON:
{{
    "market_readiness": "One sentence assessment of how ready this candidate is for the job market",
    "immediate_actions": [
        "First specific action to take this week",
        "Second specific action to take this month",
        "Third specific action for next 3 months"
    ]
}}

Be specific, honest, and actionable. No fluff.
"""

    def _parse_gap_report(self, ai_response: str) -> dict:
        try:
            cleaned = ai_response.strip()
            if "```" in cleaned:
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "market_readiness": "Analysis unavailable",
                "immediate_actions": []
            }


ai_analyzer = AIAnalyzer()