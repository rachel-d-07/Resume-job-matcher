# app/services/job_searcher.py

import time
import httpx
from typing import List, Optional
from app.core.config import settings
from app.models.job import Job, JobSearchResponse


class JobSearcher:
    """
    Fetches real job listings from Adzuna API.
    Handles pagination, rate limiting, and error recovery.
    """

    # Adzuna base URL template
    BASE_URL = (
        "https://api.adzuna.com/v1/api/jobs/"
        "{country}/search/{page}"
    )

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_WAIT = 1          # seconds — doubles each retry

    def search_jobs(
        self,
        skills: List[str],
        location: Optional[str] = "New York",
        country: Optional[str] = "us",
        page: int = 1,
        results_per_page: int = 10
    ) -> JobSearchResponse:
        """
        Main entry point.
        Builds query from skills and searches Adzuna.
        """

        # ── Build search query from skills ─────────────────────
        # Take top 5 skills to keep query focused
        top_skills = skills[:5]
        query = " ".join(top_skills)

        # ── Build API URL ───────────────────────────────────────
        url = self.BASE_URL.format(
            country=country,
            page=page
        )

        # ── Build query parameters ──────────────────────────────
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "what": query,              # job title/skills keywords
            "where": location,          # location filter
            "results_per_page": results_per_page,
            "content-type": "application/json"
        }

        # ── Make API call with retry logic ──────────────────────
        raw_response = self._make_request_with_retry(url, params)

        if raw_response is None:
            return JobSearchResponse(
                success=False,
                message="Job search failed after multiple retries.",
                total_found=0,
                page=page,
                jobs=[]
            )

        # ── Parse and normalize response ────────────────────────
        jobs = self._parse_jobs(raw_response)
        total = raw_response.get("count", 0)

        return JobSearchResponse(
            success=True,
            message=f"Found {total} jobs matching your profile.",
            total_found=total,
            page=page,
            jobs=jobs
        )

    def _make_request_with_retry(
        self,
        url: str,
        params: dict
    ) -> Optional[dict]:
        """
        Makes HTTP GET request with exponential backoff retry.
        Returns parsed JSON dict or None on complete failure.
        """
        wait_time = self.INITIAL_WAIT

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                # httpx is a modern HTTP client (like requests but async-ready)
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url, params=params)

                # ── Handle response status codes ────────────────

                if response.status_code == 200:
                    # Success — return parsed JSON
                    return response.json()

                elif response.status_code == 429:
                    # Rate limited — wait and retry
                    print(
                        f"Rate limited. Attempt {attempt}/{self.MAX_RETRIES}. "
                        f"Waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    wait_time *= 2          # exponential backoff

                elif response.status_code == 401:
                    # Bad credentials — no point retrying
                    print("Invalid Adzuna credentials. Check .env file.")
                    return None

                elif response.status_code == 400:
                    # Bad request — no point retrying
                    print(f"Bad request: {response.text}")
                    return None

                else:
                    # Unknown error — retry
                    print(
                        f"Unexpected status {response.status_code}. "
                        f"Attempt {attempt}/{self.MAX_RETRIES}"
                    )
                    time.sleep(wait_time)
                    wait_time *= 2

            except httpx.TimeoutException:
                # Request timed out — retry
                print(
                    f"Request timed out. "
                    f"Attempt {attempt}/{self.MAX_RETRIES}. "
                    f"Waiting {wait_time}s..."
                )
                time.sleep(wait_time)
                wait_time *= 2

            except httpx.RequestError as e:
                # Network error — retry
                print(f"Network error: {e}. Attempt {attempt}/{self.MAX_RETRIES}")
                time.sleep(wait_time)
                wait_time *= 2

        # All retries exhausted
        print("All retry attempts exhausted.")
        return None

    def _parse_jobs(self, response_data: dict) -> List[Job]:
        """
        Transforms raw Adzuna API response into our Job model.
        This normalization layer protects us from API changes.
        """
        jobs = []
        results = response_data.get("results", [])

        for item in results:
            try:
                # Extract salary info safely
                salary_min = None
                salary_max = None
                currency = None

                if "salary_min" in item:
                    salary_min = float(item["salary_min"])
                if "salary_max" in item:
                    salary_max = float(item["salary_max"])

                # Build normalized Job object
                job = Job(
                    id=str(item.get("id", "")),
                    title=item.get("title", "Unknown Title"),
                    company=item.get(
                        "company", {}
                    ).get("display_name", "Unknown Company"),
                    location=item.get(
                        "location", {}
                    ).get("display_name", "Unknown Location"),
                    description=item.get("description", ""),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    currency=currency,
                    job_url=item.get("redirect_url", ""),
                    posted_date=item.get("created", None),
                    contract_type=item.get("contract_type", None),
                    category=item.get(
                        "category", {}
                    ).get("label", None)
                )
                jobs.append(job)

            except Exception as e:
                # Skip malformed job entries — never crash the loop
                print(f"Skipping malformed job entry: {e}")
                continue

        return jobs


# Module-level instance
job_searcher = JobSearcher()