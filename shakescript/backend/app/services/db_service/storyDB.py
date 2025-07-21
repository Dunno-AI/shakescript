from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, List, Any
import json


class StoryDB:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    def get_all_stories(self) -> List[Dict[str, Any]]:
        result = (
            self.supabase.table("stories")
            .select("id, title, genre, is_completed")
            .execute()
        )
        return result.data if result.data else []

    def get_story_info(self, story_id: int) -> Dict:
        story_result = (
            self.supabase.table("stories").select("*").eq("id", story_id).execute()
        )
        if not story_result.data:
            return {"error": "Story not found"}
        story_row = story_result.data[0]

        episodes_result = (
            self.supabase.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .order("episode_number")
            .execute()
        )
        episodes_list = [
            {
                "id": ep["id"],
                "number": ep["episode_number"],
                "title": ep["title"],
                "content": ep["content"],
                "summary": ep["summary"],
                "emotional_state": ep.get("emotional_state", "neutral"),
                "key_events": json.loads(ep["key_events"] or "[]"),
            }
            for ep in episodes_result.data
        ]

        characters_result = (
            self.supabase.table("characters")
            .select("*")
            .eq("story_id", story_id)
            .execute()
        )
        characters = [
            {
                "Name": char["name"],
                "Role": char["role"],
                "Description": char["description"],
                "Relationship": json.loads(char["relationship"] or "{}"),
                "role_active": char.get("is_active", True),
                "Emotional_State": char.get("emotional_state", "neutral"),
                "Milestones": json.loads(char["milestones"] or "[]"),
            }
            for char in characters_result.data
        ]

        return {
            "id": story_row["id"],
            "title": story_row["title"],
            "setting": json.loads(story_row["setting"] or "{}"),
            "key_events": json.loads(story_row["key_events"] or "[]"),
            "special_instructions": story_row["special_instructions"],
            "story_outline": json.loads(story_row["story_outline"] or "[]"),
            "current_episode": story_row["current_episode"],
            "episodes": episodes_list,
            "characters": characters,
            "summary": story_row.get("summary"),
            "num_episodes": story_row["num_episodes"],
            "protagonist": json.loads(story_row["protagonist"] or "[]"),
            "timeline": json.loads(story_row["timeline"] or "[]"),
            "current_episodes_content": json.loads(
                story_row.get("current_episodes_content", "[]") or "[]"
            ),  # Add current_episodes_content
        }

    def store_story_metadata(self, metadata: Dict, num_episodes: int) -> int:
        result = (
            self.supabase.table("stories")
            .insert(
                {
                    "title": metadata.get("Title", "Untitled Story"),
                    "protagonist": json.dumps(metadata.get("Protagonist", [])),
                    "setting": json.dumps(metadata.get("Settings", {})),
                    "key_events": json.dumps([]),
                    "timeline": json.dumps([]),
                    "special_instructions": metadata.get("Special Instructions", ""),
                    "story_outline": json.dumps(metadata.get("Story Outline", [])),
                    "current_episode": 1,
                    "num_episodes": num_episodes,
                    "current_episodes_content": json.dumps(
                        []
                    ),  # Initialize current_episodes_content
                }
            )
            .execute()
        )
        story_id = result.data[0]["id"]

        character_data_list = [
            {
                "story_id": story_id,
                "name": char["Name"],
                "role": char["Role"],
                "description": char["Description"],
                "relationship": json.dumps(char.get("Relationship", {})),
                "emotional_state": char.get("Emotional_State", "neutral"),
                "is_active": True,
                "milestones": json.dumps([]),
            }
            for char in metadata.get("Characters", [])
        ]
        if character_data_list:
            self.supabase.table("characters").insert(character_data_list).execute()
        return story_id

    def update_story_current_episodes_content(
        self, story_id: int, episodes: List[Dict]
    ):
        """Update the current_episodes_content field in the stories table with refined episodes."""
        self.supabase.table("stories").update(
            {"current_episodes_content": json.dumps(episodes)}
        ).eq("id", story_id).execute()

    def get_refined_episodes(self, story_id: int) -> List[Dict]:
        """Retrieve the refined episodes from current_episodes_content if they exist."""
        story_data = self.get_story_info(story_id)
        return story_data.get("current_episodes_content", [])

    def clear_current_episodes_content(self, story_id: int):
        """Clear the current_episodes_content field after validation."""
        self.supabase.table("stories").update(
            {"current_episodes_content": json.dumps([])}
        ).eq("id", story_id).execute()

    def delete_story(self, story_id: int) -> None:
        """Delete a story from the database."""
        story = self.supabase.table("stories").select("id").eq("id", story_id).execute()
        if not story.data:
            raise ValueError(f"Story with ID {story_id} not found")

        self.supabase.table("stories").delete().eq("id", story_id).execute()
