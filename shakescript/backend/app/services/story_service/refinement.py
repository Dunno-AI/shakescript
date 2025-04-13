from typing import List, Dict, Any
from fastapi import HTTPException


def generate_and_refine_batch(
    self, story_id: int, batch_size: int, hinglish: bool, refinement_type: str
) -> List[Dict[str, Any]]:
    story_data = self.get_story_info(story_id)
    current_episode = story_data.get("current_episode", 1)
    metadata = {
        "title": story_data["title"],
        "setting": story_data["setting"],
        "key_events": story_data["key_events"],
        "special_instructions": story_data["special_instructions"],
        "story_outline": story_data["story_outline"],
        "current_episode": current_episode,
        "num_episodes": story_data["num_episodes"],
        "story_id": story_id,
        "characters": story_data["characters"],
        "hinglish": hinglish,
    }

    # Calculate number of episodes to generate in this batch
    remaining_episodes = story_data["num_episodes"] - current_episode + 1
    effective_batch_size = min(batch_size, remaining_episodes)

    # Get previous episodes for context (last 2 episodes before current batch)
    prev_episodes = []
    if current_episode > 1:
        prev_batch_end = current_episode - 1
        prev_batch_start = max(1, prev_batch_end - 2)  # Get up to 2 previous episodes
        prev_episodes = self.get_episodes_by_range(
            story_id, prev_batch_start, prev_batch_end
        )
        prev_episodes = [
            {
                "episode_number": ep["episode_number"],
                "content": ep["content"],
                "title": ep["title"],
            }
            for ep in prev_episodes
        ]

    # Generate initial batch
    episodes = self.generate_multiple_episodes(story_id, effective_batch_size, hinglish)

    # Store the initial batch in current_episodes_content and persist immediately
    story_data["current_episodes_content"] = episodes
    self.update_current_episodes_content(story_id, episodes)
    print(
        f"Generated batch for episodes {current_episode} to {current_episode + effective_batch_size - 1}"
    )

    # Apply AI refinement internally if requested
    if refinement_type == "ai":
        # Process AI refinement for this batch
        max_attempts = 3
        attempt = 0
        validation_result = {}
        while attempt < max_attempts:
            validation_result = self.ai_service.validate_batch(
                story_id, episodes, prev_episodes, metadata
            )
            if validation_result.get("status") == "success":
                print(f"Batch validated successfully on attempt {attempt+1}")
                break

            print(f"Batch needs refinement - attempt {attempt+1}")
            if validation_result.get("feedback"):
                print(f"Feedback: {validation_result.get('feedback')}")
                episodes = self.ai_service.regenerate_batch(
                    story_id,
                    validation_result["episodes"],
                    prev_episodes,
                    metadata,
                    validation_result.get("feedback", []),
                )
            attempt += 1

        if attempt == max_attempts and validation_result.get("status") != "success":
            print(
                f"AI refinement warning: Failed to refine after {max_attempts} attempts, proceeding anyway"
            )

        # Store the refined episodes to the database
        self.store_validated_episodes(story_id, episodes)

        # Update current_episode
        new_current_episode = current_episode + len(episodes)
        self.db_service.supabase.table("stories").update(
            {"current_episode": new_current_episode}
        ).eq("id", story_id).execute()

        # Clear the current_episodes_content after processing this batch
        self.clear_current_episodes_content(story_id)

        # Check if we need to process more batches
        if new_current_episode <= story_data["num_episodes"]:
            print(f"Moving to next batch starting at episode {new_current_episode}")
            # Recursively process the next batch
            next_batch = self.generate_and_refine_batch(
                story_id, batch_size, hinglish, refinement_type
            )
            # Combine with current episodes
            return episodes + next_batch

        print(f"All episodes completed: total {new_current_episode-1} episodes")
        return self.get_all_episodes(
            story_id
        )  # Return all episodes after AI refinement

    # For human refinement, just return the current batch
    return episodes
