from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class StoryCreate(BaseModel):
    prompt: str
    num_episodes: int

class StoryResponse(BaseModel):
    story_id: int
    title: str
    setting: List[Dict[str, str]]
    characters: Dict[str, Dict[str, Any]]
    key_events: List[str]
    special_instructions: str
    story_outline: Dict[str, str]
    current_episode: int
    episodes: List[Dict[str, Any]]
    summary: Optional[str] = None

class EpisodeResponse(BaseModel):
    episode_id: int
    episode_number: int
    episode_title: str
    episode_content: str
    episode_summary: str
    characters_featured: Dict[str, Dict[str, Any]]
    key_events: List[str]
    settings: List[Dict[str, str]]

class ErrorResponse(BaseModel):
    error: str
