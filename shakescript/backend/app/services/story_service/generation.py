from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
from app.services.embedding_service import EmbeddingService
import json


class StoryGeneration:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()
        self.DEFAULT_BATCH_SIZE = 2

    async def create_story(
        self, prompt: str, num_episodes: int, hinglish: bool = False
    ) -> Dict[str, Any]:
        full_prompt = f"{prompt} number of episodes = {num_episodes}"
        metadata = self.ai_service.extract_metadata(full_prompt, num_episodes, hinglish)
        print("1. Metadata extracted\n")
        if "error" in metadata:
            return metadata
        story_id = self.db_service.store_story_metadata(metadata, num_episodes)
        print("2. Story metadata stored ", story_id, "\n")
        return {"story_id": story_id, "title": metadata.get("Title", "Untitled Story")}

    def generate_and_store_episode(
        self,
        story_id: int,
        episode_number: int,
        num_episodes: int,
        hinglish: bool = False,
        prev_episodes: List = [],
    ) -> Dict[str, Any]:
        story_data = self.db_service.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        story_metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": episode_number,
            "timeline": story_data["timeline"],
        }

        episode_data = self.ai_service.generate_episode_helper(
            num_episodes,
            story_metadata,
            episode_number,
            json.dumps(story_data["characters"]),
            story_id,
            prev_episodes,
            hinglish,
        )
        print("7. Generated episode", episode_number, "\n")

        if "error" in episode_data or not episode_data.get("episode_content"):
            return {
                "error": "Failed to generate episode content",
                "episode_data": episode_data,
            }

        episode_id = self.db_service.store_episode(
            story_id, episode_data, episode_number
        )

        print("8. Episode stored\n")
        character_names = [
            char["Name"] for char in episode_data.get("characters_featured", [])
        ]
        if episode_data.get("episode_content"):
            self.embedding_service._process_and_store_chunks(
                story_id,
                episode_id,
                episode_number,
                episode_data["episode_content"],
                character_names,
            )
            print(f"Chunking completed for episode {episode_number}")
        else:
            print(f"Warning: No episode_content for episode {episode_number}")

        return {
            "episode_id": episode_id,
            "episode_number": episode_number,
            "episode_title": episode_data["episode_title"],
            "episode_content": episode_data["episode_content"],
            "episode_summary": episode_data.get("episode_summary", ""),
            "episode_emotional_state": episode_data.get(
                "episode_emotional_state", "neutral"
            ),
        }

    def generate_multiple_episodes(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
    ) -> List[Dict[str, Any]]:
        story_data = self.db_service.get_story_info(story_id)
        if "error" in story_data:
            return [story_data]

        episodes = []
        current_episode = story_data["current_episode"]
        effective_batch_size = batch_size if batch_size else self.DEFAULT_BATCH_SIZE
        for i in range(0, num_episodes, effective_batch_size):
            batch_end = min(
                current_episode + i + effective_batch_size - 1,
                current_episode + num_episodes - 1,
            )
            print("3. Last episode of this batch is ", batch_end, "\n")
            for j in range(current_episode + i, batch_end + 1):
                prev_episodes = [
                    {
                        "episode_number": ep["episode_number"],
                        "content": ep["episode_content"],
                        "title": ep["episode_title"],
                    }
                    for ep in episodes[-2:]
                ]
                print(f"4. Starting to generate episode {j} \n")
                episode_result = self.generate_and_store_episode(
                    story_id, j, num_episodes, hinglish, prev_episodes
                )
                if "error" in episode_result:
                    return episodes + [episode_result]
                episodes.append(episode_result)
        return episodes
