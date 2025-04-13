from typing import List, Dict, Any


def store_validated_episodes(
    self, story_id: int, episodes: List[Dict[str, Any]]
) -> None:
    """
    Store the validated episodes in the episodes table and update the story's current_episode.
    """
    if not episodes:
        print("No episodes to store")
        return
    
    # Store each episode in the episodes table
    for episode in episodes:
        episode_number = episode.get("episode_number")
        if not episode_number:
            print(f"Warning: Episode missing episode_number: {episode}")
            continue
            
        # Store episode in database
        episode_id = self.db_service.store_episode(story_id, episode, episode_number)
        
        # Process for embedding/chunking if needed
        character_names = [
            char["Name"] for char in episode.get("characters_featured", [])
        ] if "characters_featured" in episode else []
        
        if episode.get("episode_content"):
            self.embedding_service._process_and_store_chunks(
                story_id,
                episode_id,
                episode_number,
                episode["episode_content"],
                character_names,
            )
            print(f"Chunking completed for validated episode {episode_number}")
        else:
            print(f"Warning: No episode_content for episode {episode_number}")

    # Update the current_episode to the next number after the last validated episode
    max_episode_num = max([ep.get("episode_number", 0) for ep in episodes], default=0)
    if max_episode_num > 0:
        print(f"Updating story current_episode to {max_episode_num + 1}")
        self.db_service.supabase.table("stories").update(
            {"current_episode": max_episode_num + 1}
        ).eq("id", story_id).execute()
    
    # Clear the current_episodes field after validation
    self.clear_current_episodes_content(story_id)
