from pydantic import BaseModel
from typing import Dict, List, Any, Optional , Union


class StoryCreate(BaseModel):
    prompt: str
    num_episodes: int


class StoryResponse(BaseModel):
    story_id: int
    title: str
    setting: Dict[str, str]
    characters: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]  
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
    settings: List[Dict[str, str]]


class EpisodeCreateResponse(BaseModel):
    episode_number: int
    episode_title: str
    episode_content: str


class ErrorResponse(BaseModel):
    error: str


class StoryListItem(BaseModel):
    story_id: int
    title: str


class StoryListResponse(BaseModel):
    stories: List[StoryListItem]
