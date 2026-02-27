from pydantic import BaseModel, Field
from typing import Optional, List

class MemeMetadata(BaseModel):
    """
    Structured output from the Vision LLM analyzing a meme image.
    """
    text_caption: str = Field(
        description="The exact text written on the meme image, if any. Leave empty if none."
    )
    film_series_name: Optional[str] = Field(
        description="The name of the film, movie, or series this image is from, if recognizable. Commonly Telugu films."
    )
    year: Optional[int] = Field(
        description="The release year of the film/series, if the film was identified."
    )
    emotion: str = Field(
        description="The primary emotion or expression shown by the subject (e.g., Frustrated, Laughing, Sarcastic, Confused)."
    )
    situation: str = Field(
        description="A detailed description of the situation or context the meme represents. What kind of scenario would this meme be a good reaction for?"
    )
    keywords: List[str] = Field(
        description="5-10 keywords associated with this meme for search indexing."
    )
