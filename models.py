from pydantic import BaseModel, Field
from typing import Literal

# CONTRACT 1 — Analyze Location
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

# CONTRACT 2 — Chat
class ChatRequest(BaseModel):
    user_query: str = Field(..., min_length=1, description="Must not be empty")
    local_context: str = Field(..., min_length=1, description="Must not be empty")
    vulnerable_group: Literal["general", "farmer", "elderly", "worker", "pregnant", "child"]
    language: Literal["english", "hindi"]

# CONTRACT 3 — Verify Text (Internal)
class VerifyRequest(BaseModel):
    text_to_check: str = Field(..., min_length=20, description="Minimum 20 characters")

# CONTRACT 4 — Submit Story
class StorySubmission(BaseModel):
    author_name: str = Field(..., min_length=1, description="Must not be empty")
    latitude: float
    longitude: float
    location: str = Field(..., min_length=1, description="Must not be empty")
    story_text: str = Field(..., min_length=20, max_length=500, description="Between 20 and 500 characters")