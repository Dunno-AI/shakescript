from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
from app.services.embedding_service import EmbeddingService


class StoryService:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()

    async def create_story(self, prompt: str, num_episodes: int) -> Dict[str, Any]:
        full_prompt = f"{prompt} number of episodes = {num_episodes}"
        result = self.extract_and_store_metadata(full_prompt, num_episodes)
        if "error" in result:
            return result
        return {"story_id": result["story_id"], "title": result["title"]}

    def extract_and_store_metadata(self, user_prompt: str , num_episodes: int) -> Dict[str, Any]:
        metadata = self.ai_service.extract_metadata(user_prompt)
        if "error" in metadata:
            return metadata
        story_id = self.db_service.store_story_metadata(metadata, num_episodes)
        return {"story_id": story_id, "title": metadata.get("Title", "Untitled Story")}

    def get_story_info(self, story_id: int) -> Dict[str, Any]:
        return self.db_service.get_story_info(story_id)

    def generate_episode(
        self, story_id: int, episode_number: int, num_episodes: int
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data
        story_metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": story_data["current_episode"],
        }
        prev_episodes = []
        if episode_number > 1:
            episodes_result = (
                self.db_service.supabase.table("episodes")
                .select("episode_number, content, summary")
                .eq("story_id", story_id)
                .gte("episode_number", max(1, episode_number - 2))
                .lt("episode_number", episode_number)
                .order("episode_number", desc=True)
                .limit(2)
                .execute()
            )
            prev_episodes = [
                (ep["episode_number"], ep["content"], ep["summary"])
                for ep in episodes_result.data
            ]
        character_data = (
            self.db_service.supabase.table("characters")
            .select("*")
            .eq("story_id", story_id)
            .execute()
        )
        char_text = "\n\n".join(
            f"Name: {char['name']} Role: {char['role']} Description: {char['description']}"
            for char in character_data.data
        )
        return self.ai_service.generate_episode_helper(
            num_episodes=num_episodes,
            metadata=story_metadata,
            episode_number=episode_number,
            char_text=char_text,
            story_id=story_id,
            prev_episodes=prev_episodes,
        )

    def generate_and_store_episode(
        self, story_id: int, num_episodes: int
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data
        current_episode = story_data["current_episode"]
        episode_data = self.generate_episode(story_id, current_episode, num_episodes)
        if "error" in episode_data:
            return episode_data
        episode_id = self.db_service.store_episode(
            story_id, episode_data, current_episode
        )
        self.embedding_service._process_and_store_chunks(
            story_id,
            episode_id,
            current_episode,
            episode_data["episode_content"],
            list(episode_data.get("characters_featured", {}).keys()),
        )
        return {
            "episode_id": episode_id,
            "episode_number": current_episode,
            "episode_title": episode_data["episode_title"],
            "episode_content": episode_data["episode_content"],
            "episode_summary": episode_data["episode_summary"],
        }

    def generate_multiple_episodes(
        self, story_id: int, num_episodes: int
    ) -> List[Dict[str, Any]]:
        episodes = []
        for _ in range(num_episodes):
            episode_result = self.generate_and_store_episode(story_id, num_episodes)
            if "error" in episode_result:
                return episodes + [episode_result]
            episodes.append(episode_result)
        return episodes

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data
        episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
        instruction = f"""
        Create a comprehensive summary of the story "{story_data['title']}" based on these episode summaries:
        {episode_summaries}
        Your summary should:
        1. Capture the main storyline and character development
        2. Highlight key events that have occurred
        3. Be concise but complete (150-200 words)
        4. Not include any commentary or meta-information
        Return ONLY the summary text, no additional comments or explanations.
        """
        summary = self.ai_service.model.generate_content(instruction).text.strip()
        self.db_service.supabase.table("stories").update({"summary": summary}).eq(
            "id", story_id
        ).execute()
        return {"story_id": story_id, "summary": summary}
