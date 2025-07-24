from typing import List, Dict, Any


def generate_and_refine_batch(
    self,
    story_id: int,
    batch_size: int,
    hinglish: bool,
    refinement_type: str,
    auth_id: str,
) -> List[Dict[str, Any]]:
    story_data = self.get_story_info(story_id, auth_id)
    current_episode = story_data.get("current_episode", 1)
    print(f"Starting to generate episode from {current_episode}")

    # Calculate number of episodes to generate in this batch
    remaining_episodes = story_data["num_episodes"] - current_episode + 1
    effective_batch_size = min(batch_size, remaining_episodes)

    # Generate initial batch
    episodes = self.generate_multiple_episodes(
        story_id, current_episode, effective_batch_size, hinglish, auth_id
    )

    # Store the initial batch in current_episodes_content and persist immediately
    story_data["current_episodes_content"] = episodes
    self.update_current_episodes_content(story_id, episodes, auth_id)
    print(
        f"Generated batch for episodes {current_episode} to {current_episode + effective_batch_size - 1}"
    )

    # Apply AI refinement internally if requested
    if refinement_type == "AI":
        return self.refine_batch_by_ai(
            story_id,
            episodes,
            None,  # prev_episodes
            None,  # metadata
            story_data,
            current_episode,
            batch_size,
            refinement_type,
            hinglish,
            auth_id,
        )

    return episodes
