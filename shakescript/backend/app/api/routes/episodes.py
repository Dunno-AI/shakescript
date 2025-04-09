from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from ...models.schemas import (
    EpisodeCreateResponse,
    StoryCreate,
    StoryResponse,
    ErrorResponse,
    EpisodeResponse,
    Feedback,
)
from app.services.story_service import StoryService
from app.api.dependencies import get_story_service
from typing import Annotated, Union, Dict, Any, List

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.post(
    "/{story_id}/generate-batch",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Generate a batch of episodes for a story",
)
def generate_episode_batch(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    batch_size: int = Query(..., description="Number of episodes to generate", ge=1),
    refinement: str = Query(
        "AI", description="Refinement method: 'AI' or 'Human'", regex="^(AI|Human)$"
    ),
    hinglish: bool = Query(False, description="Generate in Hinglish if true"),
):
    """
    Generate and store a batch of episodes for a story with optional refinement.
    - `batch_size` determines the number of episodes to generate.
    - Returns a structured response with episode details or error.
    """
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    num_episodes = story_data["num_episodes"]
    current_episode = story_data["current_episode"]
    if current_episode >= num_episodes+1:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="All episodes have already been generated.",
        )

    batch_end = min(current_episode + batch_size - 1, num_episodes)

    #episodes_to_generate -> number of remaining episodes to generate
    episodes_to_generate = batch_end - current_episode + 1

    if refinement.lower() == "human":
        results = service.human_validation.process_episode_batches_with_human_feedback(
            story_id, num_episodes,hinglish, batch_size
        )
    else:  # ai
        results = service.ai_validation.process_episode_batches_with_ai_validation(
            story_id, episodes_to_generate, hinglish, batch_size
        )

    if "error" in results:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=results["error"])

    print(f"results: {results}\n")

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


@router.post(
    "/{story_id}/validate",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Validate refined episodes and update DB",
)
def validate_episodes(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    episode_numbers: List[int] = Body(...),
):
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    # Update current_episode to the next batch
    current_episode = story_data["current_episode"]
    num_episodes = story_data["num_episodes"]
    next_episode = max(current_episode, max(episode_numbers, default=0) + 1)
    service.db_service.supabase.table("stories").update(
        {"current_episode": min(next_episode, num_episodes + 1)}
    ).eq("id", story_id).execute()

    return {"status": "success", "message": "Episodes validated and updated"}


@router.post(
    "/{story_id}/feedback",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Submit feedback for episodes",
)
def submit_feedback(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    feedback: List[Feedback] = Body(...),
):
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])
    results = service.process_episode_batches_with_human_feedback(
        story_id, len(feedback), False, 2, feedback
    )
    print(f"results: {results}\n")
    return {"status": results["status"], "episodes": results["episodes"]}
