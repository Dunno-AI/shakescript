from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
from app.services.embedding_service import EmbeddingService
from app.models.schemas import StoryListItem
import json
import time

class StoryService:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()

    async def create_story(self, prompt: str, num_episodes: int, hinglish: bool = False) -> Dict[str, Any]:
        full_prompt = f"{prompt} number of episodes = {num_episodes}"
        result = self.extract_and_store_metadata(full_prompt, num_episodes, hinglish)
        return result if "error" in result else {"story_id": result["story_id"], "title": result["title"]}

    def extract_and_store_metadata(self, user_prompt: str, num_episodes: int, hinglish: bool) -> Dict[str, Any]:
        metadata = self.ai_service.extract_metadata(user_prompt, num_episodes, hinglish)
        if "error" in metadata:
            return metadata
        story_id = self.db_service.store_story_metadata(metadata, num_episodes)
        return {"story_id": story_id, "title": metadata.get("Title", "Untitled Story")}

    def get_story_info(self, story_id: int) -> Dict[str, Any]:
        return self.db_service.get_story_info(story_id)

    def generate_episode(self, story_id: int, episode_number: int, num_episodes: int, hinglish: bool = False, prev_episodes=[]) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        story_metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],  
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": episode_number,
        }
        
        char_text = json.dumps(story_data["characters"])
        return self.ai_service.generate_episode_helper(
            num_episodes=num_episodes,
            metadata=story_metadata,
            episode_number=episode_number,
            char_text=char_text,
            story_id=story_id,
            prev_episodes=prev_episodes,
            hinglish=hinglish,
        )

    def get_all_stories(self) -> List[StoryListItem]:
        return [StoryListItem(story_id=story["id"], title=story["title"]) for story in self.db_service.get_all_stories()]

    def generate_and_store_episode(self, story_id: int, episode_number: int, num_episodes: int, hinglish: bool = False, prev_episodes=[]) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        episode_generation_time = time.time()
        episode_data = self.generate_episode(story_id, episode_number, num_episodes, hinglish, prev_episodes)
        # print(f"episode {episode_number} generated in: ", time.time() - episode_generation_time)
        if "error" in episode_data:
            return episode_data

        episode_storing_time = time.time()
        episode_id = self.db_service.store_episode(story_id, episode_data, episode_number)
        self.embedding_service._process_and_store_chunks(
            story_id, episode_id, episode_number, episode_data["episode_content"], []
        )
        # print(f"episode {episode_number} stored and chunked in: ", time.time() - episode_storing_time)

        return {
            "episode_id": episode_id,
            "episode_number": episode_number,
            "episode_title": episode_data["episode_title"],
            "episode_content": episode_data["episode_content"],
            "episode_summary": episode_data.get("episode_summary", ""),
            "episode_emotional_state": episode_data.get("episode_emotional_state", "neutral"),
        }

    def generate_multiple_episodes(self, story_id: int, num_episodes: int, hinglish: bool = False) -> List[Dict[str, Any]]:
        episodes = []
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return [story_data]

        current_episode = story_data["current_episode"]

        for i in range(num_episodes):
            episode_number = current_episode + i
            prev_episodes = [
                {
                    "episode_number": ep["episode_number"],
                    "content": ep["episode_content"],
                    "summary": ep.get("episode_summary", ""),
                    "title": ep["episode_title"],
                    "emotional_state": ep.get("episode_emotional_state", "neutral"),
                }
                for ep in episodes[-2:]
            ]

            episode_result = self.generate_and_store_episode(story_id, episode_number, num_episodes, hinglish, prev_episodes)
            if "error" in episode_result:
                return episodes + [episode_result]
            
            episodes.append({
                "episode_id": episode_result["episode_id"],
                "episode_number": episode_result["episode_number"],
                "episode_title": episode_result["episode_title"],
                "episode_content": episode_result["episode_content"],
                "episode_summary": episode_result.get("episode_summary", ""),
                "episode_emotional_state": episode_result.get("episode_emotional_state", "neutral"),
            })

        # print("episodes from generate_multiple_episodes\n", episodes)
        return episodes

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
        instruction = f"""
        Create a 150-200 word audio teaser summary for "{story_data['title']}" based on these episode summaries:
        {episode_summaries}
        - Use short, vivid sentences (10-15 words) for TTS clarity.
        - Highlight key moments with dramatic phrasing (e.g., 'A howl echoed').
        - End with a hook to entice listeners (e.g., 'What’s next?').
        - Avoid complex terms or ambiguity for smooth narration.
        Return ONLY the summary text.
        """
        summary = self.ai_service.model.generate_content(instruction).text.strip()
        self.db_service.supabase.table("stories").update({"summary": summary}).eq("id", story_id).execute()
        return {"story_id": story_id, "summary": summary}


   
