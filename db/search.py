from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import Meme
from agents.embedder import generate_embedding
import logging

logger = logging.getLogger(__name__)

def search_memes(db: Session, query: str, limit: int = 20, diversify: bool = True):
    """
    Performs a hybrid/semantic search using PGVector for a given text query.
    Implements a diversity check to ensure similar templates aren't clustered together.
    """
    try:
        query_embedding = generate_embedding(query)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []
        
    # Postgres Vector Search (Semantic)
    # Cosine distance operator <->
    stmt = select(Meme).order_by(Meme.embedding.cosine_distance(query_embedding)).limit(limit * 2) # Fetch extra for diversity pruning
    
    results = db.execute(stmt).scalars().all()
    
    if not diversify:
        return results[:limit]
        
    # Diversification Logic:
    # Filter out results that share the exact same image_hash or are visually recognized as the same template
    # to provide a balanced set of different templates matching the semantic query.
    diversified_results = []
    seen_hashes = set()
    
    for meme in results:
        if len(diversified_results) >= limit:
            break
            
        if meme.image_hash and meme.image_hash in seen_hashes:
            continue # Skip duplicate template variant
            
        if meme.image_hash:
            seen_hashes.add(meme.image_hash)
            
        diversified_results.append(meme)
        
    return diversified_results
