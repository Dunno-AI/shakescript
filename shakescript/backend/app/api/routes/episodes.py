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
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Generate and optionally refine episodes for a story",
)
def generate_episode(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    hinglish: bool = Query(default=False, description="Generate in Hinglish if true"),
    all: bool = Query(
        default=False, description="Generate all remaining episodes if true"
    ),
    method: str = Query(
        default="human",
        description="Refinement method: 'human' or 'ai'",
        regex="^(human|ai)$",
    ),
):
    """
    Generate and store one or all remaining episodes for a story with optional refinement.
    - If `all=True`, generates all remaining episodes and applies refinement based on `method`.
    - Returns a structured response with episode details or error.
    """
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    num_episodes = story_data["num_episodes"]
    current_episode = story_data["current_episode"]

    if all:
        episodes_to_generate = num_episodes - current_episode + 1
        if episodes_to_generate <= 0:
            return {
                "status": "success",
                "episodes": [],
                "message": "All episodes generated",
            }
        if method.lower() == "human":
            results = service.process_episode_batches_with_human_feedback(
                story_id, episodes_to_generate, hinglish
            )
        else:  # ai
            results = service.process_episode_batches_with_ai_validation(
                story_id, episodes_to_generate, hinglish
            )
        if "error" in results:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=results["error"]
            )
        return {
            "status": results["status"],
            "episodes": [
                EpisodeCreateResponse(
                    episode_number=result["episode_number"],
                    episode_title=result["episode_title"],
                    episode_content=result["episode_content"],
                    episode_emotional_state=result.get(
                        "episode_emotional_state", "neutral"
                    ),
                )
                for result in results["episodes"]
            ],
            "message": (
                "Episodes generated and refined successfully"
                if results["status"] == "success"
                else "Generation failed"
            ),
        }
    else:
        if current_episode > num_episodes:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="All episodes have already been generated.",
            )
        prev_episodes = service.db_service.get_previous_episodes(
            story_id, current_episode, limit=2
        )
        result = service.generate_and_store_episode(
            story_id, current_episode, num_episodes, hinglish, prev_episodes
        )
        if "error" in result:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=result["error"]
            )
        return {
            "status": "success",
            "episodes": [
                EpisodeCreateResponse(
                    episode_number=result["episode_number"],
                    episode_title=result["episode_title"],
                    episode_content=result["episode_content"],
                    episode_emotional_state=result.get(
                        "episode_emotional_state", "neutral"
                    ),
                )
            ],
            "message": "Episode generated successfully",
        }
