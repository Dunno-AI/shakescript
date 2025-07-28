from fastapi import APIRouter, Depends, HTTPException, Query, Body
from starlette.status import HTTP_404_NOT_FOUND
from ...models.schemas import (
    Feedback,
    ErrorResponse,
    EpisodeBatchResponse,
)
from app.api.dependencies import get_story_service, get_current_user
from app.services.core_service import StoryService
from typing import Union, List
from fastapi import BackgroundTasks

router = APIRouter(prefix="/episodes", tags=["episodes"])

# Generate batch endpoint
@router.post(
    "/{story_id}/generate-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
    summary="Generate a batch of episodes with optional AI or human refinement",
)
async def generate_batch(
    story_id: int,
    batch_size: int = Query(1, ge=1),
    hinglish: bool = Query(False),
    refinement_type: str = Query("HUMAN", enum=["AI", "HUMAN"]),
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    story_data = service.get_story_info(story_id, auth_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episode = story_data.get("current_episode", 1)
    if current_episode > story_data.get("num_episodes", 0):
        return {"error": "All episodes generated", "episodes": []}

    episodes = service.generate_and_refine_batch(
        story_id, batch_size, hinglish, refinement_type, auth_id
    )

    if refinement_type == "AI":
        message = "All episodes generated, refined, and stored successfully"
    else:
        message = "Batch generated, awaiting human refinement"

    return {
        "status": "success",
        "episodes": episodes,
        "message": message,
    }

# Validate batch endpoint
@router.post(
    "/{story_id}/validate-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
    summary="Validate and store the current batch of episodes",
)
async def validate_batch(
    story_id: int,
    background_tasks: BackgroundTasks,
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    return service.validate_episode_batch(story_id, auth_id, background_tasks)

#refine_batch endpoint
@router.post(
    "/{story_id}/refine-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
    summary="Refine a batch of episodes based on human instructions",
)
async def refine_batch(
    story_id: int,
    feedback: List[Feedback] = Body(...),
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    return service.refine_episode_batch(story_id, feedback, auth_id)
