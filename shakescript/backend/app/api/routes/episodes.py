from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from ...models.schemas import (
    EpisodeCreateResponse,
    StoryCreate,
    StoryResponse,
    ErrorResponse,
    EpisodeResponse,
)
from app.services.story_service import StoryService
from app.api.dependencies import get_story_service
from typing import Annotated, Union, Dict, Any, List


router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.post(
    "/{story_id}/generate",
    response_model=Union[
        EpisodeCreateResponse, List[EpisodeCreateResponse], ErrorResponse
    ],
)
def generate_episode(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    hinglish: bool = Query(default=False, description="Generate in Hinglish if true"),
    all: bool = Query(
        default=False, description="Generate all remaining episodes if true"
    ),
):
    """
    Generate and store one or all remaining episodes for a story.
    """
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    num_episodes = story_data["num_episodes"]
    current_episode = story_data["current_episode"]

    if all:
        episodes_to_generate = num_episodes - current_episode + 1
        if episodes_to_generate <= 0:
            return []
        results = service.generate_multiple_episodes(
            story_id, episodes_to_generate, hinglish
        )
        if "error" in results[-1]:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=results[-1]["error"]
            )
        return [
            EpisodeCreateResponse(
                episode_number=result["episode_number"],
                episode_title=result["episode_title"],
                episode_content=result["episode_content"],
            )
            for result in results
        ]
    else:
        result = service.generate_and_store_episode(story_id, num_episodes, hinglish)
        if "error" in result:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=result["error"]
            )
        return EpisodeCreateResponse(
            episode_number=result["episode_number"],
            episode_title=result["episode_title"],
            episode_content=result["episode_content"],
        )
