from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union


class Feedback(BaseModel):
    episode_number: int
    feedback: str

    class Config:
        schema_extra = {
            "example": [
                {"episode_number": 1, "feedback": "Change title to New Title"},
                {"episode_number": 2, "feedback": "Make it more suspenseful"},
            ]
        }


class StoryCreate(BaseModel):
    prompt: str
    num_episodes: int


class StoryResponse(BaseModel):
    story_id: int
    title: str
    setting: Dict[str, str]
    characters: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
    special_instructions: str
    story_outline: List[Dict[str, str]]
    current_episode: int
    episodes: List[Dict[str, Any]]
    summary: Optional[str] = None
    protagonist: List[Dict[str, str]]
    timeline: List[Dict[str, Any]]
    batch_size: int
    refinement_method: str


class EpisodeResponse(BaseModel):
    episode_id: int
    episode_number: int
    episode_title: str
    episode_content: str
    episode_summary: str
    characters_featured: Dict[str, Dict[str, Any]]
    settings: Dict[str, str]


class EpisodeCreateResponse(BaseModel):
    episode_number: int
    episode_title: str
    episode_content: str
    episode_emotional_state: str = "neutral"


class ErrorResponse(BaseModel):
    error: str
    episodes: List[Dict[str, Any]] = []  # Added to match existing error responses


class StoryListItem(BaseModel):
    story_id: int
    title: str


class StoryListResponse(BaseModel):
    stories: List[StoryListItem]


# New model for batch response
class EpisodeBatchResponse(BaseModel):
    status: str
    episodes: List[EpisodeResponse]  # Use EpisodeResponse for typed episodes

    class Config:
        arbitrary_types_allowed = (
            True  # Allow flexibility in Dict[str, Any] within EpisodeResponse
        )
