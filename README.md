# LeadHunt: Web Scraping Lead Finder

LeadHunt is a full-stack web application designed to search for businesses by category and location, discover physical and online listings using permitted public data sources (OpenStreetMap Overpass API, Nominatim Geocoding, public business web search, and Google Places API), crawl business websites for direct contact details, and export verified leads to Excel (`.xlsx`) or CSV.

---

## Features

- **Natural-Language Search:** Accepts unstructured queries (e.g., *"List salons in Coimbatore"*, *"Hotels in Chennai"*, *"Software companies in Bangalore"*, *"Hospitals in Erode"*), deterministically parses them into category and location, and maps them to standard business features.
- **Permitted Public Data Sources:** Discovers physical POIs from OpenStreetMap's Overpass & Nominatim engines and business websites from public search engines without bypassing anti-bot or CAPTCHA restrictions.
- **Deep Contact Crawler:** Asynchronously parses website HTML, Schema.org JSON-LD structured data (`LocalBusiness`, `Organization`, `Place`), meta tags, `tel:`/`mailto:` links, social handles, and Google Maps listings. Crawls contact pages (`/contact`, `/about`) when details are absent on the homepage.
- **Data Quality & Deduplication:**
  - Standardizes phone numbers to clean digits and validates strict email syntax.
  - Validates 6-digit Indian PIN codes and address structures.
  - Deduplicates records by normalized phone numbers and `name + city`.
  - Merges duplicate listings so the final lead retains maximum contact completeness.
  - Assigns a deterministic completeness confidence score (0% to 100%).
- **Results Dashboard:** Clean, responsive dark-mode interface built with React, TypeScript, and Tailwind CSS.
  - Live pipeline progress bar with current execution stage.
  - Searchable, sortable, paginated leads table.
  - Direct links to websites, phone dials, emails, and Google Maps listings.
- **Excel & CSV Export:** Download results formatted in Excel (`.xlsx`) with navy headers, auto-fitted columns, thin borders, and clickable hyperlinks, or download UTF-8 with BOM CSV files.
- **Search History:** Persistent search job history to revisit past jobs, view previously scraped leads, or download exports.

---

## Tech Stack

- **Frontend:** React 19, TypeScript, Tailwind CSS, Lucide React, Vite.
- **Backend:** Python FastAPI, Pydantic v2, SQLAlchemy 2.0 (async).
- **Database:** PostgreSQL (with automatic SQLite fallback for local developer setups).
- **Scraping & Extraction:** HTTPX (async, rate-limited, bounded concurrency), BeautifulSoup4, lxml, Playwright.
- **Exporting:** Pandas, OpenPyXL.
- **Deployment:** Docker, Docker Compose, Nginx reverse proxy.

---

## Quick Start with Docker Compose

Run the entire application (PostgreSQL + FastAPI backend + Nginx React frontend):

```bash
docker compose up --build
```

- **Web Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database:** PostgreSQL running on port `5432`

---

## Local Development (Without Docker)

The backend automatically detects if PostgreSQL is listening on port 5432. If not running, it gracefully initializes SQLite at `leadhunt.db`.

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Configuration (`.env`)

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/leadhunt` | PostgreSQL connection string |
| `MAX_CONCURRENCY` | `5` | Maximum concurrent website crawling requests |
| `REQUEST_TIMEOUT_SECONDS` | `15` | Scraping HTTP request timeout |
| `GOOGLE_PLACES_API_KEY` | *(Empty)* | Optional Google Maps Platform Places API Key |

---

## API Endpoints

- `POST /api/v1/jobs` - Trigger an asynchronous lead scraping job.
- `GET /api/v1/jobs` - List past scraping jobs.
- `GET /api/v1/jobs/{id}` - Get status, pipeline progress, and scraper logs for a job.
- `DELETE /api/v1/jobs/{id}` - Delete a search job and its associated leads.
- `GET /api/v1/jobs/{id}/leads` - Retrieve paginated, filtered, and sorted leads for a job.
- `GET /api/v1/export/jobs/{id}?format=xlsx|csv` - Download lead results as `.xlsx` or `.csv`.
- `GET /api/v1/stats` - Summary counts of total jobs, leads, phones, emails, and websites.
