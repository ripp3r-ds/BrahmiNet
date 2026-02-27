import instructor
from openai import AsyncOpenAI
from .schemas import MemeMetadata
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# We configure the client. It can point to OpenAI or any OpenAI-compatible endpoint (like Gemini via proxy or directly if supported).
# For best vision results, gpt-4o or gemini-1.5-pro are ideal.
client = instructor.from_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))

async def analyze_meme_image(image_url: str, model: str = "gpt-4o") -> Optional[MemeMetadata]:
    """
    Analyzes a meme image (via URL) and returns structured metadata including emotion, situation, and text captions.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Check environment variables.")
        return None

    try:
        response = await client.chat.completions.create(
            model=model,
            response_model=MemeMetadata,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in South Indian pop culture, specifically Telugu cinema and memes. "
                        "Your task is to analyze meme templates, predominantly featuring Brahmanandam and other actors. "
                        "Identify the text, the film, the emotion, context, and what situations it would be a perfect reaction for."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please analyze this meme image and extract the metadata."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ],
                }
            ],
        )
        return response
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None
