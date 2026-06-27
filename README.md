<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=32&pause=1000&color=6C63FF&center=true&vCenter=true&width=600&lines=AI+Resume+%E2%86%92+Job+Matching+Agent;Built+with+FastAPI+%2B+Gemini+AI;From+Resume+to+Ranked+Jobs+in+Seconds" alt="Typing SVG" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-upcoming-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-upcoming-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

[![Status](https://img.shields.io/badge/Status-Active%20Development-FFD700?style=flat-square)]()
[![Phases](https://img.shields.io/badge/Phases%20Complete-5%20of%2010-6C63FF?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)]()

<br/>

> **Upload your resume. Get ranked, AI-explained job matches. Instantly.**
>
> An end-to-end AI agent that parses your resume, searches real job listings,
> scores each one against your profile, and tells you exactly why each job fits — or doesn't.

<br/>

[**View API Docs →**](http://localhost:8000/docs) · [**Report a Bug**](https://github.com/rachel-d-07/Resume-job-matcher/issues) · [**Follow Progress**](#-build-progress)

</div>

---

## 🎬 How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   📄 Upload Resume (PDF/DOCX)                                       │
│          │                                                          │
│          ▼                                                          │
│   🔍 Text Extraction  ──────►  PyMuPDF / python-docx               │
│          │                                                          │
│          ▼                                                          │
│   🤖 AI Skill Extraction  ──►  Gemini 1.5 Flash                    │
│          │                                                          │
│          │   { skills, experience, education }                      │
│          ▼                                                          │
│   🌐 Real Job Search  ──────►  Adzuna API (millions of jobs)       │
│          │                                                          │
│          ▼                                                          │
│   ⚡ Match & Rank Engine  ──►  Keyword + Title + Location scoring   │
│          │                                                          │
│          ▼                                                          │
│   💡 AI Explains Match  ───►  "Why this job fits you" (Phase 6)    │
│          │                                                          │
│          ▼                                                          │
│   ✉️  Cover Letter  ────────►  Personalized per job (Phase 7)      │
│          │                                                          │
│          ▼                                                          │
│   🖥️  Streamlit UI  ────────►  Clean web interface (Phase 8)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚦 Build Progress

> Built **phase by phase** following production engineering practices — not a tutorial clone.

| # | Phase | What It Does | Status |
|---|-------|-------------|--------|
| 1 | **Project Architecture** | System design, folder structure, requirements | ✅ Done |
| 2 | **Resume Upload** | PDF/DOCX upload, type & size validation, error handling | ✅ Done |
| 3 | **Resume Parsing** | Text extraction + Gemini AI skill/experience extraction | ✅ Done |
| 4 | **Job Search Integration** | Adzuna API, pagination, rate limiting, exponential backoff | ✅ Done |
| 5 | **Matching Engine** | Keyword scoring, title relevance, location matching, ranking | ✅ Done |
| 6 | **AI Analysis Layer** | Gemini explains each match, skill gap report | 🔄 In Progress |
| 7 | **Cover Letter Generator** | Personalized, company-specific cover letters | ⏳ Next |
| 8 | **Streamlit Frontend** | Full web UI with country selector and results dashboard | ⏳ Upcoming |
| 9 | **PostgreSQL Integration** | Save resumes, searches, match history | ⏳ Upcoming |
| 10 | **Docker + Deployment** | Containerization, production deployment | ⏳ Upcoming |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI | REST API with auto-generated docs |
| **AI / LLM** | Google Gemini 1.5 Flash | Resume parsing + match explanation |
| **PDF Parsing** | PyMuPDF (fitz) | Fast, accurate text extraction |
| **DOCX Parsing** | python-docx | Word document text extraction |
| **Job Search** | Adzuna API | Real job listings across 12+ countries |
| **Data Validation** | Pydantic v2 | Typed models, request/response validation |
| **HTTP Client** | httpx | Async-ready API calls with retry logic |
| **Config** | pydantic-settings | Environment-based configuration |
| **Frontend** | Streamlit *(upcoming)* | Web interface |
| **Database** | PostgreSQL *(upcoming)* | Persistent storage |
| **Deployment** | Docker *(upcoming)* | Containerized production build |

---

## 📡 API Endpoints

```
GET   /health              →  System health check
POST  /resume/upload       →  Upload PDF or DOCX (up to 10MB)
POST  /resume/parse        →  AI extracts skills, experience, education
POST  /jobs/search         →  Search real jobs by skills + country
POST  /match/jobs          →  Search + score + rank in one call  ← Main endpoint
```

### Example: Match Jobs Request

```bash
curl -X POST "http://localhost:8000/match/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "experience_titles": ["ML Engineer"],
    "location": "New York",
    "country": "us",
    "results_per_page": 10
  }'
```

### Example: Match Jobs Response

```json
{
  "success": true,
  "message": "Analyzed 10 jobs. Top match: Excellent Match",
  "total_jobs_analyzed": 10,
  "matched_jobs": [
    {
      "job": {
        "title": "AI/ML Engineer",
        "company": "QTech US Inc",
        "location": "New York, NY",
        "salary_min": 140000,
        "job_url": "https://www.adzuna.com/..."
      },
      "match_score": 0.81,
      "match_percentage": 81,
      "matched_skills": ["Python", "Machine Learning"],
      "missing_skills": ["FastAPI"],
      "match_label": "Excellent Match"
    }
  ]
}
```

---

## 📁 Project Structure

```
resume_job_matcher/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── resume.py        # Upload & parse endpoints
│   │       ├── jobs.py          # Job search endpoint
│   │       └── match.py         # Match & rank endpoint
│   │
│   ├── core/
│   │   └── config.py            # Centralized env config
│   │
│   ├── models/
│   │   ├── resume.py            # Resume data models
│   │   ├── job.py               # Job data models
│   │   └── match.py             # Match result models
│   │
│   ├── services/
│   │   ├── resume_parser.py     # PDF/DOCX text extraction
│   │   ├── skill_extractor.py   # Gemini AI skill extraction
│   │   ├── job_searcher.py      # Adzuna API + retry logic
│   │   └── job_matcher.py       # Scoring & ranking engine
│   │
│   └── main.py                  # FastAPI app entry point
│
├── uploads/                     # Temporary file storage
├── .env.example                 # Environment variable template
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Gemini API key — [Get free key →](https://aistudio.google.com/app/apikey)
- Adzuna API credentials — [Register free →](https://developer.adzuna.com/)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/rachel-d-07/Resume-job-matcher.git
cd Resume-job-matcher

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and add your API keys

# 5. Start the server
uvicorn app.main:app --reload
```

### Open API Docs

```
http://localhost:8000/docs
```

---

## 🔑 Environment Variables

```env
APP_NAME=ResumeJobMatcher
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads

# AI
GEMINI_API_KEY=your_gemini_key_here

# Job Search
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key
ADZUNA_COUNTRY=us
ADZUNA_RESULTS_PER_PAGE=10
```

### Supported Job Search Countries

| Country | Code | Country | Code |
|---------|------|---------|------|
| 🇺🇸 USA | `us` | 🇬🇧 UK | `gb` |
| 🇮🇳 India | `in` | 🇨🇦 Canada | `ca` |
| 🇦🇺 Australia | `au` | 🇩🇪 Germany | `de` |

---

## 🧠 Architecture Decisions

> Every decision here was made intentionally and can be explained in interviews.

**Why FastAPI over Flask/Django?**
Async-native, auto-generates OpenAPI docs, Pydantic integration out of the box, and 3x faster than Flask for I/O-bound workloads.

**Why two-step parsing (extract text → AI)?**
Sending raw PDF bytes to an LLM is expensive and unreliable. Extracting text locally first is free and deterministic — AI only sees clean input.

**Why a separate matching engine instead of just asking AI to rank?**
Speed and cost. Scoring 90 jobs with pure AI would cost ~90 API calls. Our engine scores all 90 in milliseconds, then AI only explains the top matches.

**Why normalize Adzuna responses into a `Job` model?**
Decoupling. If we swap Adzuna for Indeed tomorrow, the rest of the system doesn't change. Only the fetcher changes.

---

## 👨‍💻 Author

**Kennoy** — MSc AI & ML Student

Building production-ready AI systems from scratch, one phase at a time.

[![GitHub](https://img.shields.io/badge/GitHub-rachel--d--07-181717?style=for-the-badge&logo=github)](https://github.com/rachel-d-07)

---

## 📌 Engineering Philosophy

This project follows real production practices:

- ✅ **Separation of concerns** — routes, services, and models are strictly separated
- ✅ **Graceful degradation** — every failure returns a valid response, never a crash
- ✅ **Environment-based config** — zero hardcoded values anywhere
- ✅ **Git hygiene** — `.env` protected, meaningful commit messages per phase
- ✅ **Typed contracts** — every request and response is a validated Pydantic model
- ✅ **Retry logic** — exponential backoff on all external API calls

---

<div align="center">

**⭐ Star this repo if you find it useful — it helps others discover it.**

*Active development — new phases pushed regularly.*

</div>