from fastapi import APIRouter, Depends, HTTPException, status, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from ...models.schemas import StoryCreate, StoryListResponse, StoryResponse, ErrorResponse, EpisodeResponse
from app.services.story_service import StoryService
from app.api.dependencies import get_story_service
from typing import Annotated, Union, Dict, Any, List

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/all", response_model=Union[StoryListResponse, ErrorResponse])
def get_all_stories(service: StoryService = Depends(get_story_service)):
    """
    Retrieve a list of all stories.
    """
    stories = service.get_all_stories()
    return StoryListResponse(stories=stories)


@router.post("/", response_model=Union[StoryResponse, ErrorResponse])
async def create_story(
    story: StoryCreate, service: Annotated[StoryService, Depends(get_story_service)]
):
    result = await service.create_story(story.prompt, story.num_episodes)
    if "error" in result:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["error"])

    story_info = service.get_story_info(result["story_id"])
    if "error" in story_info:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=story_info["error"])

    return StoryResponse(
        story_id=story_info["id"],
        title=story_info["title"],
        setting=story_info["setting"],
        characters=story_info.get("characters", {}),
        special_instructions=story_info["special_instructions"],
        story_outline=story_info["story_outline"],
        current_episode=story_info["current_episode"],
        episodes=story_info["episodes"],
        summary=story_info.get("summary"),
    )


@router.get("/{story_id}", response_model=Union[StoryResponse, ErrorResponse])
def get_story(story_id: int, service: StoryService = Depends(get_story_service)):
    """
    Retrieve detailed information about a story.
    """
    story_info = service.get_story_info(story_id)
    if "error" in story_info:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=story_info["error"])

    return StoryResponse(
        story_id=story_info["id"],
        title=story_info["title"],
        setting=story_info["setting"],
        characters=story_info.get("characters", {}),
        special_instructions=story_info["special_instructions"],
        story_outline=story_info["story_outline"],
        current_episode=story_info["current_episode"],
        episodes=story_info["episodes"],
        summary=story_info.get("summary"),
    )

@router.post("/{story_id}/summary", response_model=Union[Dict[str, Any], ErrorResponse])
def update_story_summary(
    story_id: int, service: Annotated[StoryService, Depends(get_story_service)]
):
    """
    Update the summary of a story based on its episodes.
    """
    result = service.update_story_summary(story_id)
    if "error" in result:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["error"])
    return result



