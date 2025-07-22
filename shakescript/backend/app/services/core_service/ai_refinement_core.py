def refine_batch_by_ai(
    self,
    story_id,
    episodes,
    batch_size,
    refinement_type,
    hinglish,
    auth_id: str,
):
    max_attempts = 3
    attempt = 0
    validation_result = {}
    story_data = self.get_story_info(story_id, auth_id)
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

    # Get previous episodes for context (last 2 episodes before current batch)
    prev_episodes = []
    if current_episode > 1:
        prev_batch_end = current_episode - 1
        prev_batch_start = max(1, prev_batch_end - 2)  # Get up to 2 previous episodes
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

    self.store_validated_episodes(story_id, episodes, auth_id)

    # Update current_episode
    new_current_episode = current_episode + len(episodes)
    self.db_service.supabase.table("stories").update(
        {"current_episode": new_current_episode}
    ).eq("id", story_id).eq("auth_id", auth_id).execute()

    self.clear_current_episodes_content(story_id, auth_id)

    # Check if we need to process more batches
    if new_current_episode <= story_data["num_episodes"]:
        print(f"Moving to next batch starting at episode {new_current_episode}")
        # Recursively process the next batch
        next_batch = self.generate_and_refine_batch(
            story_id, batch_size, hinglish, refinement_type, auth_id
        )
        return episodes + next_batch

    print(f"All episodes completed: total {new_current_episode-1} episodes")
    return self.get_all_episodes(story_id, auth_id)
