import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# We use text-embedding-3-small as it's highly performant and extremely cheap for the 100-1000 requests/day scale. 
# It produces 1536-dimensional vectors, matching our PGVector schema.
embedder = None
if os.getenv("OPENAI_API_KEY"):
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")
else:
    print("Warning: OPENAI_API_KEY not set. Embeddings will not work.")

def generate_embedding(text_content: str) -> list[float]:
    """
    Generates a 1536-dimensional float vector for the given text.
    For memes, we combine the Extracted Context + Keywords + Situation to form the embedding text.
    """
    if not embedder:
        raise ValueError("Embedder not configured. Missing API keys.")
    
    # Langchain OpenAIEmbeddings has an embed_query method
    return embedder.embed_query(text_content)
