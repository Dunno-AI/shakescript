from fastapi import APIRouter, Depends, HTTPException, Query, Body
from starlette.status import HTTP_404_NOT_FOUND
from pydantic import BaseModel
from ...models.schemas import (
    Feedback,
    ErrorResponse,
    EpisodeBatchResponse,
)
from app.api.dependencies import get_story_service
from app.services.story_service import StoryService
from ...services.ai_service import AIService
from typing import Union, List, Dict

router = APIRouter(prefix="/episodes", tags=["episodes"])


# Generate batch endpoint
@router.post(
    "/{story_id}/generate-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
    summary="Generate a batch of episodes with optional AI or human refinement",
)
async def generate_batch(
    story_id: int,
    batch_size: int = Query(2, ge=1),
    hinglish: bool = Query(False),
    refinement_type: str = Query("ai", enum=["ai", "human"]),
    service: StoryService = Depends(get_story_service),
):
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episode = story_data.get("current_episode", 1)
    if current_episode > story_data.get("num_episodes", 0):
        return {"error": "All episodes generated", "episodes": []}

    episodes = service.generate_and_refine_batch(
        story_id, batch_size, hinglish, refinement_type
    )

    # For AI refinement, return all episodes
    # For human refinement, return just the batch
    if refinement_type == "ai":
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
    service: StoryService = Depends(get_story_service),
):
    story_data = service.get_story_info(story_id)
    print(f"Story data keys: {list(story_data.keys())}")

    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episodes_content = story_data.get("current_episodes_content", [])
    print(f"Current episodes found: {len(current_episodes_content)}")

    # Debug the structure if episodes exist
    if current_episodes_content:
        print(
            f"Sample episode structure: {list(current_episodes_content[0].keys()) if current_episodes_content else 'None'}"
        )

    if not current_episodes_content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No batch found to validate"
        )

    # Store the validated episodes (implicit approval)
    service.store_validated_episodes(story_id, current_episodes_content)

    # Update the current episode number
    max_episode = max(
        [ep.get("episode_number", 0) for ep in current_episodes_content], default=0
    )
    next_episode = max_episode + 1

    # Check completion status
    if next_episode <= story_data.get("num_episodes", 0):
        return {
            "status": "success",
            "episodes": [],
            "message": "Batch validated and stored. Ready for next batch generation.",
        }
    else:
        return {
            "status": "success",
            "episodes": [],
            "message": "All episodes validated and stored. Story complete.",
        }


@router.post(
    "/{story_id}/refine-batch",
    response_model=Union[EpisodeBatchResponse, ErrorResponse],
    summary="Refine a batch of episodes based on human instructions",
)
async def refine_batch(
    story_id: int,
    feedback: List[Feedback] = Body(...),
    service: StoryService = Depends(get_story_service),
):
    story_data = service.get_story_info(story_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    # Get the current episodes content
    current_episodes_content = story_data.get("current_episodes_content", [])
    if not current_episodes_content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No current batch found to refine"
        )

    # Extract episode numbers from feedback
    episode_numbers = [fb.episode_number for fb in feedback]

    # Create metadata for refinement
    metadata = {
        "title": story_data["title"],
        "setting": story_data["setting"],
        "key_events": story_data.get("key_events", []),
        "special_instructions": story_data.get("special_instructions", ""),
        "story_outline": story_data.get("story_outline", []),
        "current_episode": story_data.get("current_episode", 1),
        "num_episodes": story_data.get("num_episodes", 0),
        "story_id": story_id,
        "characters": story_data.get("characters", {}),
        "hinglish": story_data.get("hinglish", False),
    }

    # Get previous episodes for context
    prev_batch_start = max(1, metadata["current_episode"] - 3)
    prev_batch_end = metadata["current_episode"] - 1
    prev_episodes = []
    if prev_batch_end >= prev_batch_start:
        prev_episodes = service.get_episodes_by_range(
            story_id, prev_batch_start, prev_batch_end
        )

        print(f"Previous episodes found: {prev_episodes}")

        prev_episodes = [
            {
                "episode_number": ep["episode_number"],
                "content": ep["content"], 
                "title": ep["title"],
            }
            for ep in prev_episodes
        ]

    # Create AI service
    ai_service = AIService()

    # Regenerate the whole batch with feedback
    refined_episodes = ai_service.regenerate_batch(
        story_id,
        current_episodes_content,
        prev_episodes,
        metadata,
        [
            {"episode_number": fb.episode_number, "feedback": fb.feedback}
            for fb in feedback
        ],
    )

    # Store the refined episodes
    service.update_current_episodes_content(story_id, refined_episodes)

    return {
        "status": "pending",
        "episodes": refined_episodes,
        "message": f"Batch refined with feedback, awaiting validation",
    }
