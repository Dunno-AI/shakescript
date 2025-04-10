from typing import Dict, List, Any
from app.services.story_service.regeneration_service import RegenerationService
from app.services.db_service import DBService
import json


class AIValidation:
    def __init__(self):
        self.regeneration_service = RegenerationService()
        self.db_service = DBService()
        self.DEFAULT_BATCH_SIZE = 2

    def process_episode_batches_with_ai_validation(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
        max_retries: int = 5,
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
            "current_episode": story_data.get("current_episode", 1),
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

        all_episodes = []

        while current_batch_start <= num_episodes:
            batch_end = min(
                current_batch_start + effective_batch_size - 1, num_episodes
            )
            print(f"Generating batch from episode {current_batch_start} to {batch_end}")

            batch_valid = False
            current_batch = []
            retry_count = 0
            feedback = None

            while not batch_valid and retry_count < max_retries:
                initial_batch = self.regeneration_service._regenerate_batch(
                    story_id,
                    current_batch_start,
                    batch_end,
                    metadata,
                    prev_episodes + all_episodes,
                    hinglish,
                    feedback=feedback,  # Using feedback in generation
                )

                validation_result = self.regeneration_service._validate_batch(
                    initial_batch, metadata
                )
                batch_valid = validation_result.get("valid", False)

                if batch_valid:
                    current_batch = initial_batch
                    print(f"Batch {current_batch_start}-{batch_end} is valid.")
                else:
                    retry_count += 1
                    feedback = validation_result.get("feedback", [])
                    print(
                        f"Batch {current_batch_start}-{batch_end} is invalid. Retrying ({retry_count}/{max_retries})..."
                    )
                    print("Feedback:", feedback)

            if not batch_valid:
                print(
                    f"Max retries reached for batch {current_batch_start}-{batch_end}. Skipping this batch."
                )
                current_batch_start = batch_end + 1
                continue

            stored_batch = self.regeneration_service._store_batch_after_validation(
                story_id, current_batch
            )

            all_episodes.extend(stored_batch)
            current_batch_start = batch_end + 1

            self.db_service.supabase.table("stories").update(
                {"current_episode": min(current_batch_start, num_episodes + 1)}
            ).eq("id", story_id).execute()

        return (
            {"status": "success", "episodes": all_episodes}
            if all_episodes
            else {"error": "No episodes generated", "episodes": []}
        )
