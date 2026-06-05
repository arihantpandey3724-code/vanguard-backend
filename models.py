from pydantic import BaseModel, Field
from typing import Optional

# CONTRACT 1
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

# CONTRACT 2
class ChatRequest(BaseModel):
    user_query: str = Field(..., min_length=1)
    local_context: str = Field(..., min_length=1)

# CONTRACT 3
class VerifyRequest(BaseModel):
    text_to_check: str = Field(..., min_length=20)

# CONTRACT 4
class StorySubmission(BaseModel):
    author_name: str = Field(..., min_length=1)
    latitude: Optional[float] = None # Allow nulls
    longitude: Optional[float] = None # Allow nulls
    location: str = Field(..., min_length=1)
    story_text: str = Field(..., min_length=20, max_length=500)