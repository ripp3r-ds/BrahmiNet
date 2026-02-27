import logging
from sqlalchemy.orm import Session
from utils.dedupe import generate_phash, check_duplicate_url, check_duplicate_phash, find_similar_vector
from agents.vision_agent import analyze_meme_image
from agents.embedder import generate_embedding
from utils.r2_storage import upload_image
from db.models import Meme
import requests
from io import BytesIO
import uuid

logger = logging.getLogger(__name__)

async def process_new_meme(db: Session, source_url: str) -> dict:
    """
    Core pipeline to process a new meme from a URL.
    Returns a dict with status and details.
    """
    # 1. Exact URL Check
    if check_duplicate_url(db, source_url):
        logger.info(f"Duplicate URL found: {source_url}")
        return {"status": "skipped", "reason": "url_duplicate"}

    # 2. Download & Hash
    phash = generate_phash(source_url)
    if not phash:
        return {"status": "error", "reason": "download_failed"}
        
    if check_duplicate_phash(db, phash):
        logger.info(f"Duplicate image hash found for: {source_url}")
        return {"status": "skipped", "reason": "phash_duplicate"}

    # 3. Vision Extraction
    metadata = await analyze_meme_image(source_url)
    if not metadata:
        return {"status": "error", "reason": "vision_analysis_failed"}
        
    # 4. Generate Embeddings based off rich context
    combined_text = f"Text: {metadata.text_caption} | Film: {metadata.film_series_name} ({metadata.year}) | Emotion: {metadata.emotion} | Situation: {metadata.situation} | Keywords: {', '.join(metadata.keywords)}"
    embedding = generate_embedding(combined_text)
    
    # 5. Vector Similarity Check (Variant Detection)
    similar_meme = find_similar_vector(db, embedding, threshold=0.92)
    if similar_meme:
        logger.info(f"Similar variant detected (ID: {similar_meme.id}) for URL: {source_url}")
        # Could implement quality overwrite logic here. For now, we skip or label it a variant.
        # Let's skip to keep the DB clean unless we explicitly want variants.
        # return {"status": "skipped", "reason": "vector_variant_duplicate"}

    # 6. Upload to R2
    # Download again since generate_phash consumes the stream.
    resp = requests.get(source_url)
    file_obj = BytesIO(resp.content)
    r2_key = f"memes/{uuid.uuid4()}.jpg" # Simplify extension handling for now
    
    upload_success = upload_image(file_obj, r2_key)
    if not upload_success:
        return {"status": "error", "reason": "r2_upload_failed"}

    # 7. Save to DB
    new_meme = Meme(
        source_url=source_url,
        r2_key=r2_key,
        text_caption=metadata.text_caption,
        film_series_name=metadata.film_series_name,
        year=metadata.year,
        emotion=metadata.emotion,
        situation=metadata.situation,
        image_hash=phash,
        embedding=embedding
    )
    
    try:
        db.add(new_meme)
        db.commit()
        db.refresh(new_meme)
        return {"status": "success", "meme_id": new_meme.id}
    except Exception as e:
        db.rollback()
        logger.error(f"DB Insert Failed: {e}")
        return {"status": "error", "reason": "db_insert_failed"}
