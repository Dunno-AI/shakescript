from typing import Dict, List, Any
from app.services.story_service.regeneration_service import RegenerationService
from app.services.db_service import DBService
from app.models.schemas import Feedback
import json


class HumanValidation:
    def __init__(self):
        self.regeneration_service = RegenerationService()
        self.db_service = DBService()
        self.DEFAULT_BATCH_SIZE = 2

    def process_episode_batches_with_human_feedback(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
        feedback: List[Dict[str, Any]] = [],
    ) -> Dict[str, Any]:
        story_data = self.db_service.get_story_info(story_id)
        if "error" in story_data:
            return {"error": story_data["error"], "episodes": []}

        metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": story_data["current_episode"],
            "num_episodes": num_episodes,
            "story_id": story_id,
            "characters": story_data["characters"],
            "hinglish": hinglish,
        }

        prev_episodes = story_data["episodes"]
        current_batch_start = story_data["current_episode"]
        effective_batch_size = batch_size if batch_size else self.DEFAULT_BATCH_SIZE

        if current_batch_start > num_episodes:
            return {"error": "All episodes generated", "episodes": []}

        batch_end = min(current_batch_start + effective_batch_size - 1, num_episodes)
        
        print(f"9. Started Regeneration with human feedback {current_batch_start} - {batch_end} \n")
        # Use the feedback directly as it's now in the correct format
        refined_batch = self.regeneration_service._regenerate_batch(
            story_id,
            current_batch_start,
            batch_end,
            metadata,
            prev_episodes,
            hinglish,
            feedback=feedback,
        )

        self.db_service.supabase.table("stories").update(
            {"current_episode": min(batch_end + 1, num_episodes + 1)}
        ).eq("id", story_id).execute()
        print("12. Regeneration complete.\n")
        return (
            {"status": "success", "episodes": refined_batch}
            if refined_batch
            else {"error": "No episodes refined", "episodes": []}
        )

    def _process_api_feedback(
        self, feedback_list: List[Feedback]
    ) -> List[Dict[str, Any]]:
        """
        Transforms API feedback list into the format expected by regeneration_service.
        Each item in the returned list should have:
        {
            "episode_number": int,
            "feedback": str
        }
        """
        processed_feedback = []
        for fb in feedback_list:
            feedback_item = {
                "episode_number": fb.episode_number,
                "feedback": fb.feedback,
            }
            processed_feedback.append(feedback_item)

        return processed_feedback
