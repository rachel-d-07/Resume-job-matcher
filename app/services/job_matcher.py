# app/services/job_matcher.py

import re
from typing import List, Tuple
from app.models.job import Job
from app.models.match import MatchedJob


class JobMatcher:
    """
    Scores and ranks jobs against a candidate profile.
    Uses weighted combination of keyword, title, and location matching.
    """

    # Scoring weights — must sum to 1.0
    KEYWORD_WEIGHT = 0.50     # skill keyword overlap
    TITLE_WEIGHT   = 0.35     # job title relevance
    LOCATION_WEIGHT = 0.15    # location preference

    # Match label thresholds
    EXCELLENT_THRESHOLD = 0.75
    GOOD_THRESHOLD      = 0.50
    FAIR_THRESHOLD      = 0.25

    def match_and_rank(
        self,
        candidate_skills: List[str],
        candidate_titles: List[str],
        candidate_location: str,
        jobs: List[Job]
    ) -> List[MatchedJob]:
        """
        Main entry point.
        Scores every job and returns them ranked best to worst.
        """

        if not jobs:
            return []

        matched_jobs = []

        for job in jobs:
            # Score this job against the candidate
            matched_job = self._score_job(
                job=job,
                candidate_skills=candidate_skills,
                candidate_titles=candidate_titles,
                candidate_location=candidate_location
            )
            matched_jobs.append(matched_job)

        # Sort by match_score descending (best first)
        matched_jobs.sort(
            key=lambda x: x.match_score,
            reverse=True
        )

        return matched_jobs

    def _score_job(
        self,
        job: Job,
        candidate_skills: List[str],
        candidate_titles: List[str],
        candidate_location: str
    ) -> MatchedJob:
        """
        Scores a single job against the candidate profile.
        Returns MatchedJob with score and reasoning.
        """

        # ── 1. Keyword Score ───────────────────────────────────
        keyword_score, matched_skills, missing_skills = (
            self._keyword_score(candidate_skills, job)
        )

        # ── 2. Title Score ─────────────────────────────────────
        title_score = self._title_score(candidate_titles, job.title)

        # ── 3. Location Score ──────────────────────────────────
        location_score = self._location_score(
            candidate_location,
            job.location
        )

        # ── 4. Weighted Final Score ────────────────────────────
        final_score = (
            keyword_score  * self.KEYWORD_WEIGHT +
            title_score    * self.TITLE_WEIGHT   +
            location_score * self.LOCATION_WEIGHT
        )

        # Clamp between 0.0 and 1.0
        final_score = max(0.0, min(1.0, final_score))

        # ── 5. Human readable label ────────────────────────────
        label = self._get_match_label(final_score)

        return MatchedJob(
            job=job,
            match_score=round(final_score, 4),
            match_percentage=round(final_score * 100),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_label=label
        )

    def _keyword_score(
        self,
        candidate_skills: List[str],
        job: Job
    ) -> Tuple[float, List[str], List[str]]:
        """
        Measures skill overlap between candidate and job.
        Searches both title and description.

        Returns:
            score          → 0.0 to 1.0
            matched_skills → skills found in job
            missing_skills → skills NOT found in job
        """

        if not candidate_skills:
            return 0.0, [], []

        # Combine job text for searching
        job_text = (
            f"{job.title} {job.description}"
        ).lower()

        matched = []
        missing = []

        for skill in candidate_skills:
            # Use word boundary matching for accuracy
            # "Java" should not match "JavaScript"
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, job_text):
                matched.append(skill)
            else:
                missing.append(skill)

        # Score = proportion of candidate skills found in job
        score = len(matched) / len(candidate_skills)

        return score, matched, missing

    def _title_score(
        self,
        candidate_titles: List[str],
        job_title: str
    ) -> float:
        """
        Checks if the job title matches candidate's experience titles.
        Uses partial matching for flexibility.

        Example:
            Candidate title: "ML Engineer"
            Job title: "Senior ML Engineer" → match
        """

        if not candidate_titles or not job_title:
            return 0.3      # neutral score if no data

        job_title_lower = job_title.lower()

        # Common title keywords that indicate relevance
        ai_ml_keywords = [
            "machine learning", "ml", "ai", "artificial intelligence",
            "data scientist", "data science", "deep learning",
            "nlp", "computer vision", "python developer",
            "software engineer", "backend", "full stack",
            "data engineer", "mlops", "research"
        ]

        # Check if job title contains any AI/ML keywords
        for keyword in ai_ml_keywords:
            if keyword in job_title_lower:
                return 0.8      # strong title match

        # Check against candidate's own titles
        for title in candidate_titles:
            title_words = title.lower().split()
            for word in title_words:
                if len(word) > 3 and word in job_title_lower:
                    return 0.6  # partial title match

        return 0.2              # weak title match

    def _location_score(
        self,
        candidate_location: str,
        job_location: str
    ) -> float:
        """
        Scores location compatibility.
        Remote jobs always score high.
        """

        if not candidate_location or not job_location:
            return 0.5          # neutral if unknown

        candidate_loc = candidate_location.lower()
        job_loc = job_location.lower()

        # Remote jobs match everyone
        if "remote" in job_loc:
            return 1.0

        # Exact or partial location match
        # Extract city/country from candidate location
        candidate_parts = candidate_loc.replace(",", " ").split()

        for part in candidate_parts:
            if len(part) > 2 and part in job_loc:
                return 0.9      # location match

        # Same country at least
        # Check last word (usually country)
        if candidate_parts and candidate_parts[-1] in job_loc:
            return 0.6

        return 0.2              # different location

    def _get_match_label(self, score: float) -> str:
        """
        Converts numeric score to human readable label.
        """
        if score >= self.EXCELLENT_THRESHOLD:
            return "Excellent Match"
        elif score >= self.GOOD_THRESHOLD:
            return "Good Match"
        elif score >= self.FAIR_THRESHOLD:
            return "Fair Match"
        else:
            return "Low Match"


# Module-level instance
job_matcher = JobMatcher()