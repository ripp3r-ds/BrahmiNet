from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import engine, Base
from sqlalchemy import text
from db import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enable pgvector extension and create tables
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic if any

from fastapi.middleware.cors import CORSMiddleware
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, Query
from db.search import search_memes
from utils.cache import cache_search_results

app = FastAPI(title="BrahmiNet Meme RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "BrahmiNet API is running"}

@app.get("/search")
@cache_search_results(ttl_seconds=3600)
async def search(query: str = Query(..., min_length=2), limit: int = 15, diversify: bool = True, db: Session = Depends(get_db)):
    """
    Search memes by semantic meaning or keywords.
    """
    results = search_memes(db, query, limit=limit, diversify=diversify)
    return [
        {
            "id": m.id,
            "r2_url": f"https://your-r2-public-url/{m.r2_key}", # In production, format this correctly
            "text_caption": m.text_caption,
            "film_series": m.film_series_name,
            "year": m.year,
            "emotion": m.emotion,
            "situation": m.situation
        }
        for m in results
    ]

