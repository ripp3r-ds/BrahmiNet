# BrahmiNet Action Center

Welcome to the BrahmiNet Action Center! This document provides simple explanations of the project, answers your questions about the current implementation status, and guides you on how to run it.

## 1. Implementation Status Check
**Are all phases (1-6) implemented?**
- **Phase 1 (Setup):** Mostly done. The DB (Neon+pgvector) is connected, R2 credentials exist, and dependencies are defined. This action center document is part of Phase 1!
- **Phase 2 (Database/Storage):** Done. SQLAlchemy models (`db/models.py`) and R2 utilities (`utils/r2_storage.py`) are implemented.
- **Phase 3 (Agents & Ingestion):** Partially done. The crawling agents (`scraper.py`), vision agent (`vision_agent.py`), embedder, and pipeline logic (`pipeline/ingestion.py`) **are written**. **Missing:** The Async Task Queue (Celery/Redis) is not wired up yet, meaning ingestion doesn't run automatically.
- **Phase 4 (Hybrid Search):** Done. Vector/SQL search is in `db/search.py`, and the `/search` endpoint is exposed in `main.py` with Upstash Redis caching.
- **Phase 5 (Search UI):** Done. A React/Vite app is scaffolded in the `frontend` directory with routing setup.
- **Phase 6 (Twitter Bot):** Done. The polling logic and Meme RAG integration exist in `agents/twitter_bot.py`.

## 2. Ingestion: Where and How it Happens
- **Where:** `pipeline/ingestion.py` in the `process_new_meme()` function.
- **What triggers what?**
  **Currently, NOTHING triggers the ingestion automatically.** 
  We have written the standalone scrapers (Twitter, Instagram) and the ingestion pipeline that processes a single URL, but they are not connected to a scheduler. 
  **Next Step Required:** You need to set up a Celery worker or FastAPI Background Tasks that runs on a schedule (e.g., every 6 hours), calls `TwitterScraper`, gets a list of meme URLs, and loops over them, calling `process_new_meme()` for each one.

## 3. Required Environment Variables (`.env`)
Make sure your `.env` contains the following. *(Some are currently missing from your existing `.env`!)*

**Database & Redis**
- `NEON_DATABASE_URL` 
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

**Storage**
- `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET_NAME`

**AI Agents**
- `OPENAI_API_KEY` or `GOOGLE_API_KEY` (Required for `vision_agent.py` and `embedder.py`)
- `TENOR_API_KEY` (For scraping GIFs from Tenor)

**Twitter Bot / Scraper**
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
- `TWITTER_BEARER_TOKEN`
- `TWITTER_BOT_USER_ID`

## 4. How to Run the Code

### Step 1: Initialize Environment
We are using `uv` for lightning-fast python environment management and `npm` for the frontend.
```bash
# Backend Setup
pip install uv
uv venv
# On Windows, activate with: .venv\Scripts\activate
uv pip install -r requirements.txt

# Frontend Setup
cd frontend
npm install
```

### Step 2: Start the Backend (API Server)
From the root directory, start the FastAPI app:
```bash
# Ensure your virtual environment is activated
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`. You can check `http://localhost:8000/health`.

### Step 3: Start the Frontend
In a new terminal, navigate to the `frontend` folder and start the React app:
```bash
cd frontend
npm run dev
```
The UI will be available at `http://localhost:5173`.

### Step 4: (Optional) Run the Twitter Bot Locally
To run the bot in polling mode:
```bash
python -m agents.twitter_bot
```
