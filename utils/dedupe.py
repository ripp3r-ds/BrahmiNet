import imagehash
from PIL import Image
import requests
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import Meme

def generate_phash(image_url: str) -> str:
    """Download image and generate perceptual hash."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return str(imagehash.phash(img))
    except Exception as e:
        print(f"Error generating phash for {image_url}: {e}")
        return ""

def check_duplicate_url(db: Session, source_url: str) -> bool:
    """Stage 1: Check if the exact URL already exists."""
    if not source_url:
        return False
    meme = db.execute(select(Meme).where(Meme.source_url == source_url)).scalar_one_or_none()
    return meme is not None

def check_duplicate_phash(db: Session, phash: str) -> Meme | None:
    """Stage 2: Check for exact/near-exact visual duplicates using perceptual hash."""
    if not phash:
        return None
    return db.execute(select(Meme).where(Meme.image_hash == phash)).scalar_one_or_none()

def find_similar_vector(db: Session, embedding: list[float], threshold: float = 0.90) -> Meme | None:
    """
    Stage 3: Check for semantic variants using PGVector cosine distance.
    Distance represents 1 - cosine_similarity. So lower distance = higher similarity.
    Threshold 0.90 similarity means distance <= 0.10.
    """
    if not embedding:
        return None
    # pgvector cosine distance operator is <->
    # We find the closest match.
    stmt = select(Meme).order_by(Meme.embedding.cosine_distance(embedding)).limit(1)
    closest_meme = db.execute(stmt).scalar_one_or_none()
    
    if closest_meme and closest_meme.embedding:
        # Calculate actual similarity to see if it passes threshold (requires recalculation or relying on distance in query)
        # Using SQLAlchemy distance calculation in query is better:
        distance_stmt = select(Meme.embedding.cosine_distance(embedding)).where(Meme.id == closest_meme.id)
        distance = db.execute(distance_stmt).scalar()
        if distance is not None and (1 - distance) >= threshold:
            return closest_meme
    return None
