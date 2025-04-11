from typing import Dict, List, Any
from app.services.db_service import DBService
from app.services.ai_service import AIService
from app.models.schemas import StoryListItem


class StoryUtils:
    def __init__(self):
        self.db_service = DBService()
        self.ai_service = AIService()

    def get_story_info(self, story_id: int) -> Dict[str, Any]:
        return self.db_service.get_story_info(story_id)

    def get_all_stories(self) -> List[StoryListItem]:
        return [
            StoryListItem(story_id=story["id"], title=story["title"])
            for story in self.db_service.get_all_stories()
        ]

    def _update_story_memory(
        self, story_id: int, episode_data: Dict, story_memory: Dict
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

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return {"error": story_data["error"]}
        episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
        instruction = f"Create a 150-200 word audio teaser summary for '{story_data['title']}' based on: {episode_summaries}. Use vivid, short sentences. End with a hook."
        summary = self.ai_service.model.generate_content(instruction).text.strip()
        self.db_service.supabase.table("stories").update({"summary": summary}).eq(
            "id", story_id
        ).execute()
        return {"status": "success", "summary": summary}
