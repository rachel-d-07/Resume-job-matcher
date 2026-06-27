# app/services/job_searcher.py

import time
import httpx
from typing import List, Optional
from app.core.config import settings
from app.models.job import Job, JobSearchResponse


class JobSearcher:
    BASE_URL = (
        "https://api.adzuna.com/v1/api/jobs/"
        "{country}/search/{page}"
    )
    MAX_RETRIES = 3
    INITIAL_WAIT = 1

    def search_jobs(
        self,
        skills: List[str],
        location: Optional[str] = "New York",
        country: Optional[str] = "us",
        page: int = 1,
        results_per_page: int = 10
    ) -> JobSearchResponse:

        top_skills = skills[:2]
        query = " ".join(top_skills)

        url = self.BASE_URL.format(
            country=country,
            page=page
        )

        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "what": query,
            "where": location,
            "results_per_page": results_per_page,
            "content-type": "application/json"
        }

        # DEBUG prints
        print(f"DEBUG → query: {query}")
        print(f"DEBUG → url: {url}")
        print(f"DEBUG → location: {location}, country: {country}")
        print(f"DEBUG → app_id: {settings.ADZUNA_APP_ID[:4]}...")

        raw_response = self._make_request_with_retry(url, params)

        print(f"DEBUG → raw_response is None: {raw_response is None}")
        if raw_response:
            print(f"DEBUG → jobs in response: {raw_response.get('count', 0)}")

        if raw_response is None:
            return JobSearchResponse(
                success=False,
                message="Job search failed after multiple retries.",
                total_found=0,
                page=page,
                jobs=[]
            )

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

        wait_time = self.INITIAL_WAIT

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url, params=params)

                print(f"DEBUG → status code: {response.status_code}")

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429:
                    print(f"Rate limited. Attempt {attempt}/{self.MAX_RETRIES}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= 2

                elif response.status_code == 401:
                    print("Invalid Adzuna credentials. Check .env file.")
                    print(f"DEBUG → response body: {response.text}")
                    return None

                elif response.status_code == 400:
                    print(f"Bad request: {response.text}")
                    return None

                else:
                    print(f"Unexpected status {response.status_code}. Attempt {attempt}/{self.MAX_RETRIES}")
                    print(f"DEBUG → response body: {response.text[:300]}")
                    time.sleep(wait_time)
                    wait_time *= 2

            except httpx.TimeoutException:
                print(f"Request timed out. Attempt {attempt}/{self.MAX_RETRIES}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                wait_time *= 2

            except httpx.RequestError as e:
                print(f"Network error: {e}. Attempt {attempt}/{self.MAX_RETRIES}")
                time.sleep(wait_time)
                wait_time *= 2

        print("All retry attempts exhausted.")
        return None

    def _parse_jobs(self, response_data: dict) -> List[Job]:

        jobs = []
        results = response_data.get("results", [])

        for item in results:
            try:
                salary_min = None
                salary_max = None

                if "salary_min" in item:
                    salary_min = float(item["salary_min"])
                if "salary_max" in item:
                    salary_max = float(item["salary_max"])

                job = Job(
                    id=str(item.get("id", "")),
                    title=item.get("title", "Unknown Title"),
                    company=item.get("company", {}).get("display_name", "Unknown Company"),
                    location=item.get("location", {}).get("display_name", "Unknown Location"),
                    description=item.get("description", ""),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    currency=None,
                    job_url=item.get("redirect_url", ""),
                    posted_date=item.get("created", None),
                    contract_type=item.get("contract_type", None),
                    category=item.get("category", {}).get("label", None)
                )
                jobs.append(job)

            except Exception as e:
                print(f"Skipping malformed job entry: {e}")
                continue

        return jobs


job_searcher = JobSearcher()