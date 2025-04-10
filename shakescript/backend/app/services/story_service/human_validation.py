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
        feedback: List[Feedback] = [],
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
        changes = self._process_api_feedback(feedback, prev_episodes)

        refined_batch = self.regeneration_service._regenerate_batch(
            story_id,
            current_batch_start,
            batch_end,
            metadata,
            prev_episodes,
            hinglish,
            feedback,
        )

        self.db_service.supabase.table("stories").update(
            {"current_episode": min(batch_end + 1, num_episodes + 1)}
        ).eq("id", story_id).execute()

        return (
            {"status": "success", "episodes": refined_batch}
            if refined_batch
            else {"error": "No episodes refined", "episodes": []}
        )

    def _process_api_feedback(
        self, feedback: List[Feedback], episodes: List[Dict]
    ) -> Dict[int, List[Dict]]:
        changes = {}
        for fb in feedback:
            ep_num = fb.episode_number
            if ep_num in [ep["number"] for ep in episodes]:
                changes[ep_num] = [
                    {
                        "type": (
                            "content"
                            if not fb.feedback.startswith("Change title")
                            else "title"
                        ),
                        "value": (
                            fb.feedback.split("to ")[-1]
                            if "Change title" in fb.feedback
                            else fb.feedback
                        ),
                        "instruction": fb.feedback,
                    }
                ]
        return changes
