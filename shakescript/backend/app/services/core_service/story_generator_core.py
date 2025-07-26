from typing import Dict, List, Any
from fastapi import HTTPException
import json


async def create_story(
    self,
    prompt: str,
    num_episodes: int,
    refinement_method: str,
    hinglish: bool = False,
    auth_id: str = "",
) -> Dict[str, Any]:
    full_prompt = f"{prompt} number of episodes = {num_episodes}"
    metadata = self.ai_service.extract_metadata(full_prompt, num_episodes, hinglish)
    if "error" in metadata:
        return metadata
    story_id = self.db_service.store_story_metadata(
        metadata, num_episodes, refinement_method, auth_id
    )
    return {"story_id": story_id, "title": metadata.get("Title", "Untitled Story")}


def generate_multiple_episodes(
    self,
    story_id: int,
    start_episode: int,
    num_episodes: int = 1,
    hinglish: bool = False,
    auth_id: str = "",
) -> List[Dict[str, Any]]:
    """
    Generate one or multiple episodes for a story,with rate limiting
    """
    limit_check = self.db_service.check_and_update_episode_limits(auth_id)
    if "error" in limit_check:
        # This will stop execution and send a clear error to the frontend.
        raise HTTPException(status_code=429, detail=limit_check["error"])

    story_data = self.db_service.get_story_info(story_id, auth_id)
    if "error" in story_data:
        return [story_data]

    # Determine starting episode number
    current_episode = start_episode

    story_metadata = {
        "title": story_data["title"],
        "setting": story_data["setting"],
        "key_events": story_data["key_events"],
        "special_instructions": story_data["special_instructions"],
        "story_outline": story_data["story_outline"],
        "timeline": story_data["timeline"],
    }

    episodes = []

    for i in range(num_episodes):
        episode_number = current_episode + i

        prev_episodes = [
            {
                "episode_number": ep["episode_number"],
                "content": ep["episode_content"],
                "title": ep["episode_title"],
            }
            for ep in episodes[-2:]
        ]

        story_metadata["current_episode"] = episode_number

        episode_data = self.ai_service.generate_episode_helper(
            num_episodes,
            story_metadata,
            episode_number,
            json.dumps(story_data["characters"]),
            story_id,
            prev_episodes,
            hinglish,
            auth_id=auth_id,
        )

        if "error" in episode_data or not episode_data.get("episode_content"):
            error_result = {
                "error": "Failed to generate episode content",
                "episode_number": episode_number,
                "episode_data": episode_data,
            }
            return episodes + [error_result]

        episode_id = self.db_service.store_episode(
            story_id, episode_data, episode_number, auth_id
        )

        if episode_data.get("episode_content"):
            character_names = [
                char["Name"] for char in episode_data.get("characters_featured", [])
            ]
            self.embedding_service._process_and_store_chunks(
                story_id,
                episode_id,
                episode_number,
                episode_data["episode_content"],
                character_names,
                auth_id=auth_id,
            )
            print(f"Chunking completed for episode {episode_number}")
        else:
            print(f"Warning: No episode_content for episode {episode_number}")

        episode_result = {
            "episode_id": episode_id,
            "episode_number": episode_number,
            "episode_title": episode_data["episode_title"],
            "episode_content": episode_data["episode_content"],
            "episode_summary": episode_data.get("episode_summary", ""),
            "episode_emotional_state": episode_data.get(
                "episode_emotional_state", "neutral"
            ),
        }

        episodes.append(episode_result)

    return episodes
