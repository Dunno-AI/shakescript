from typing import List, Dict
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from app.models.schemas import Feedback

def refine_episode_batch(
    self,
    story_id: int,
    feedback: List[Feedback],
    auth_id: str
) -> Dict:
    """
    Logic for refining the episode batch
    """
    story_data = self.get_story_info(story_id, auth_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episodes_content = story_data.get("current_episodes_content", [])
    if not current_episodes_content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No current batch found to refine"
        )

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

    prev_batch_start = max(1, metadata["current_episode"] - 3)
    prev_batch_end = metadata["current_episode"] - 1
    prev_episodes = []
    if prev_batch_end >= prev_batch_start:
        prev_episodes = self.db_service.get_episodes_by_range(
            story_id, prev_batch_start, prev_batch_end, auth_id
        )
        prev_episodes = [
            {
                "episode_number": ep["episode_number"],
                "content": ep["content"], 
                "title": ep["title"],
            }
            for ep in prev_episodes
        ]


    refined_episodes = self.ai_service.regenerate_batch(
        story_id,
        current_episodes_content,
        prev_episodes,
        metadata,
        [{"episode_number": fb.episode_number, "feedback": fb.feedback} for fb in feedback],
        auth_id
    )

    self.update_current_episodes_content(story_id, refined_episodes, auth_id)

    return {
        "status": "pending",
        "episodes": refined_episodes,
        "message": "Batch refined with feedback, awaiting validation",
    }


def validate_episode_batch(
    self,
    story_id: int,
    auth_id: str,
    background_tasks
) -> Dict:
    """
    Logic for validating the episode batch
    """
    story_data = self.get_story_info(story_id, auth_id)
    if "error" in story_data:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=story_data["error"])

    current_episodes_content = story_data.get("current_episodes_content", [])
    if not current_episodes_content:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No batch found to validate"
        )

    total_episodes = story_data["num_episodes"]
    self.store_validated_episodes(story_id, current_episodes_content, total_episodes, auth_id, background_tasks)

    max_episode = max([ep.get("episode_number", 0) for ep in current_episodes_content], default=0)
    next_episode = max_episode + 1

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
