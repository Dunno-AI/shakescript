from typing import Dict, List, Any
from app.models.schemas import StoryListItem


def get_story_info(self, story_id: int, auth_id: str) -> Dict[str, Any]:
    return self.db_service.get_story_info(story_id, auth_id)


def get_all_stories(self, auth_id: str) -> List[StoryListItem]:
    return [
        StoryListItem(
            story_id=story["id"],
            title=story["title"],
            genre=story["genre"],
            is_completed=story["is_completed"],
        )
        for story in self.db_service.get_all_stories(auth_id)
    ]


def _update_story_memory(
    self, story_id: int, episode_data: Dict, story_memory: Dict, auth_id: str
):
    if story_id not in story_memory:
        story_memory[story_id] = {
            "characters": {},
            "key_events": [],
            "settings": {},
            "arcs": [],
        }
    memory = story_memory[story_id]
    memory["characters"].update(
        {char["Name"]: char for char in episode_data.get("characters_featured", [])}
    )
    memory["key_events"].extend(episode_data.get("Key Events", []))
    memory["settings"].update(episode_data.get("Settings", {}))
    memory["arcs"].append(
        {
            "episode_number": episode_data["episode_number"],
            "phase": episode_data.get("current_phase", "Unknown"),
        }
    )


def update_story_summary(self, story_id: int, auth_id: str) -> Dict[str, Any]:
    story_data = self.get_story_info(story_id, auth_id)
    if "error" in story_data:
        return {"error": story_data["error"]}
    episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
    instruction = f"Create a 150-200 word audio teaser summary for '{story_data['title']}' based on: {episode_summaries}. Use vivid, short sentences. End with a hook."
    summary = self.ai_service.model.generate_content(instruction).text.strip()
    self.client.table("stories").update({"summary": summary}).eq("id", story_id).eq(
        "auth_id", auth_id
    ).execute()
    return {"status": "success", "summary": summary}


def store_validated_episodes(
    self, story_id: int, episodes: List[Dict[str, Any]], total_episodes: int, auth_id: str
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
        episode_id = self.db_service.store_episode(
            story_id, episode, episode_number, auth_id
        )

        # Process for embedding/chunking if needed
        character_names = (
            [char["Name"] for char in episode.get("characters_featured", [])]
            if "characters_featured" in episode
            else []
        )

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

    max_episode_num = max([ep.get("episode_number", 0) for ep in episodes], default=0)
    is_completed = True if max_episode_num == total_episodes else False
    if max_episode_num > 0:
        self.client.table("stories").update(
            {"current_episode": max_episode_num + 1, "is_completed": is_completed}
        ).eq("id", story_id).eq("auth_id", auth_id).execute()
        print(f"Updated story current_episode to {max_episode_num + 1}")

    # Clear the current_episodes field after validation
    self.clear_current_episodes_content(story_id, auth_id)
