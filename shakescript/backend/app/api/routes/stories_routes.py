from fastapi import APIRouter, Body, Depends, HTTPException, status
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from ...models.schemas import (
    StoryListResponse,
    StoryResponse,
    ErrorResponse,
    StoryListItem,  # Import StoryListItem
)
from app.services.core_service import StoryService
from app.api.dependencies import get_story_service, get_current_user
from typing import Annotated, Union, Dict, Any, List
from app.utils import parse_user_prompt

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get(
    "/all",
    response_model=Union[StoryListResponse, ErrorResponse],
    summary="Retrieve all stories",
)
def get_all_stories(
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    """
    Retrieve a list of all stories with a structured response for the authenticated user.
    """
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )

    stories_from_db = service.get_all_stories(auth_id)

    # --- FIX: Manually construct the list of StoryListItem objects ---
    # This ensures the data structure matches the Pydantic model perfectly.
    stories_for_response = [
        StoryListItem(
            story_id=story.get("id"),
            title=story.get("title"),
            genre=story.get("genre"),
            is_completed=story.get("is_completed"),
        )
        for story in stories_from_db
    ]

    return (
        {"status": "success", "stories": stories_for_response}
        if stories_for_response
        else {"status": "success", "stories": [], "message": "No stories found"}
    )


# ... (the rest of your stories_routes.py file remains the same) ...
@router.post(
    "/",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Create a new story",
)
async def create_story(
    service: Annotated[StoryService, Depends(get_story_service)],
    prompt: str = Body(..., description="Detailed story idea or prompt"),
    num_episodes: int = Body(..., description="Total number of episodes", ge=1),
    batch_size: int = Body(
        1, description="Number of episodes to generate per batch", ge=1
    ),
    refinement: str = Body(
        "AI", description="Refinement method: 'AI' or 'Human'", regex="^(AI|HUMAN)$"
    ),
    hinglish: bool = Body(False, description="Generate in Hinglish if true"),
    user: dict = Depends(get_current_user),
):
    prompt = parse_user_prompt(prompt)
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )

    result = await service.create_story(
        prompt, num_episodes, refinement, hinglish, auth_id
    )
    if "error" in result:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["error"])

    story_info = service.get_story_info(result["story_id"], auth_id)
    if "error" in story_info:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=story_info["error"])

    story_for_response = StoryResponse(
        story_id=story_info.get("id"),
        title=story_info.get("title"),
        setting=story_info.get("setting"),
        characters=story_info.get("characters", {}),
        special_instructions=story_info.get("special_instructions"),
        story_outline=story_info.get("story_outline"),
        current_episode=story_info.get("current_episode"),
        episodes=story_info.get("episodes", []),
        summary=story_info.get("summary"),
        protagonist=story_info.get("protagonist"),
        timeline=story_info.get("timeline"),
        batch_size=batch_size,
        refinement_method=refinement,
        total_episodes=story_info.get("num_episodes"),
    )

    return {
        "status": "success",
        "story": story_for_response,
        "message": "Story created successfully",
    }


@router.get(
    "/{story_id}",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Retrieve a specific story",
)
def get_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )

    story_info = service.get_story_info(story_id, auth_id)
    if "error" in story_info:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=story_info["error"])

    story_for_response = StoryResponse(
        story_id=story_info.get("id"),
        title=story_info.get("title"),
        setting=story_info.get("setting"),
        characters=story_info.get("characters", {}),
        special_instructions=story_info.get("special_instructions"),
        story_outline=story_info.get("story_outline"),
        current_episode=story_info.get("current_episode"),
        episodes=story_info.get("episodes", []),
        summary=story_info.get("summary"),
        protagonist=story_info.get("protagonist"),
        timeline=story_info.get("timeline"),
        batch_size=story_info.get("batch_size", 1),
        refinement_method=story_info.get("refinement_method", "AI"),
        total_episodes=story_info.get("num_episodes"),
    )

    return {
        "status": "success",
        "story": story_for_response,
        "message": "Story retrieved successfully",
    }


@router.post(
    "/{story_id}/summary",
    response_model=Union[Dict[str, Any], ErrorResponse],
    summary="Update story summary",
)
def update_story_summary(
    story_id: int,
    service: Annotated[StoryService, Depends(get_story_service)],
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )

    result = service.update_story_summary(story_id, auth_id)
    if "error" in result:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["error"])
    return {"status": "success", **result, "message": "Summary updated successfully"}


@router.delete(
    "/{story_id}",
    response_model=Dict[str, str],
    summary="Delete a story and all associated data",
)
def delete_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    try:
        auth_id = user.get("auth_id")
        if not auth_id:
            raise HTTPException(
                status_code=403, detail="Could not identify user from token."
            )

        service.delete_story(story_id, auth_id)
        return {
            "message": f"Story {story_id} and all associated data deleted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete story: {str(e)}")


@router.post(
    "/{story_id}/complete",
    response_model=Dict[str, str],
    summary="Mark a story as completed",
)
def complete_story(
    story_id: int,
    service: StoryService = Depends(get_story_service),
    user: dict = Depends(get_current_user),
):
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )
    service.set_story_completed(story_id, True, auth_id)
    return {"status": "success", "message": f"Story {story_id} marked as completed."}
