from fastapi import APIRouter, Depends, HTTPException, Query, Body
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from pydantic import BaseModel
from ...models.schemas import (
    Feedback,
    ErrorResponse,
    EpisodeBatchResponse,
    EpisodeResponse,
)
from app.services.story_service.human_validation import HumanValidation
from app.services.story_service.ai_validation import AIValidation
from app.services.story_service.regeneration_service import RegenerationService
from app.services.story_service import StoryService
from typing import Annotated, Union, List, Dict

router = APIRouter(prefix="/episodes", tags=["episodes"])


def get_human_validation_service():
    return HumanValidation()


def get_ai_validation_service():
    return AIValidation()


def get_regeneration_service():
    return RegenerationService()


def get_story_service():
    return StoryService()


@router.post(
    "/{story_id}/generate-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
)
def generate_batch(
    story_id: int,
    batch_size: int = Query(2, ge=1),
    refinement: str = Query("ai", regex="^(ai|human)$"),
    hinglish: bool = Query(False),
    service: Annotated[StoryService, Depends(get_story_service)] = None,
):
    db_service = service.db_service if service else StoryService().db_service
    story_data = db_service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episode = story_data["current_episode"]
    batch_end = min(current_episode + batch_size - 1, story_data["num_episodes"])
    if current_episode > story_data["num_episodes"]:
        return {"error": "All episodes generated", "episodes": []}

    if refinement == "ai":
        ai_service = AIValidation()
        result = ai_service.process_episode_batches_with_ai_validation(
            story_id, story_data["num_episodes"], hinglish, batch_size
        )
        # Ensure result conforms to EpisodeBatchResponse
        return (
            {
                "status": result["status"],
                "episodes": [
                    EpisodeResponse(
                        episode_id=(
                            int(ep["episode_id"])
                            if ep.get("episode_id") is not None
                            else 0
                        ),  # Default to 0 if None
                        episode_number=(
                            int(ep["episode_number"])
                            if ep.get("episode_number") is not None
                            else 0
                        ),
                        episode_title=ep.get("episode_title", ""),
                        episode_content=ep.get("episode_content", ""),
                        episode_summary=ep.get("episode_summary", ""),
                        characters_featured=ep.get("characters_featured", {}),
                        settings=ep.get("settings", {}),
                    )
                    for ep in result["episodes"]
                ],
            }
            if "status" in result
            else result
        )
    else:  # human
        episodes = (
            service.generate_multiple_episodes(
                story_id, batch_size, hinglish, batch_size
            )
            if service
            else StoryService().generate_multiple_episodes(
                story_id, batch_size, hinglish, batch_size
            )
        )
        # Convert raw episode dicts to EpisodeResponse instances with type safety
        formatted_episodes = [
            EpisodeResponse(
                episode_id=int(
                    ep.get("episode_id", 0)
                ),  # Default to 0 if None or missing
                episode_number=int(
                    ep.get("episode_number", 0)
                ),  # Default to 0 if None or missing
                episode_title=ep.get("episode_title", ""),
                episode_content=ep.get("episode_content", ""),
                episode_summary=ep.get("episode_summary", ""),
                characters_featured=ep.get("characters_featured", {}),
                settings=ep.get("settings", {}),
            )
            for ep in episodes
        ]
        return {"status": "success", "episodes": formatted_episodes}


@router.post(
    "/{story_id}/validate", response_model=Union[EpisodeBatchResponse, ErrorResponse]
)
def validate_episodes(
    story_id: int,
    service: Annotated[HumanValidation, Depends(get_human_validation_service)],
    feedback: List[Feedback] = Body(...),
):
    story_data = service.db_service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episode = story_data["current_episode"]
    batch_end = min(
        current_episode + service.DEFAULT_BATCH_SIZE - 1, story_data["num_episodes"]
    )
    result = service.process_episode_batches_with_human_feedback(
        story_id,
        story_data["num_episodes"],
        False,
        service.DEFAULT_BATCH_SIZE,
        feedback,
    )
    # Ensure result conforms to EpisodeBatchResponse with type safety
    return (
        {
            "status": result["status"],
            "episodes": [
                EpisodeResponse(
                    episode_id=int(ep.get("episode_id", 0)),
                    episode_number=int(ep.get("episode_number", 0)),
                    episode_title=ep.get("episode_title", ""),
                    episode_content=ep.get("episode_content", ""),
                    episode_summary=ep.get("episode_summary", ""),
                    characters_featured=ep.get("characters_featured", {}),
                    settings=ep.get("settings", {}),
                )
                for ep in result["episodes"]
            ],
        }
        if "status" in result
        else result
    )
