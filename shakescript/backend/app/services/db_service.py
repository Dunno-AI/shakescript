from supabase import create_client, Client
from app.core.config import settings
from typing import Dict
import json

class DBService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    def get_story_info(self, story_id: int) -> Dict:
        """Get information about a story, including characters."""
        story_result = (
            self.supabase.table("stories").select("*").eq("id", story_id).execute()
        )
        if not story_result.data or len(story_result.data) == 0:
            return {"error": "Story not found"}
        story_row = story_result.data[0]

        episodes_result = (
            self.supabase.table("episodes")
            .select("id, episode_number, title, content, summary")
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
            }
            for ep in episodes_result.data
        ]

        characters_result = (
            self.supabase.table("characters")
            .select("*")
            .eq("story_id", story_id)
            .execute()
        )
        characters = {
            char["name"]: {
                "Name": char["name"],
                "Role": char["role"],
                "Description": char["description"],
                "Relationship": (
                    json.loads(char["relationship"]) if char["relationship"] else {}
                ),
                "role_active": char["is_active"],
            }
            for char in characters_result.data
        }

        setting = json.loads(story_row["setting"]) if story_row["setting"] else []
        key_events = (
            json.loads(story_row["key_events"]) if story_row["key_events"] else []
        )
        story_outline = (
            json.loads(story_row["story_outline"]) if story_row["story_outline"] else {}
        )

        return {
            "id": story_row["id"],
            "title": story_row["title"],
            "setting": setting,
            "characters": characters,
            "key_events": key_events,
            "special_instructions": story_row["special_instructions"],
            "story_outline": story_outline,
            "current_episode": story_row["current_episode"],
            "episodes": episodes_list,
            "summary": story_row.get("summary"),
            "num_episodes": story_row["num_episodes"],
        }

    def store_story_metadata(self, metadata: Dict, num_episodes: int) -> int:
        """Store story metadata and return the story ID."""
        setting = json.dumps(metadata.get("Settings", []))
        key_events = json.dumps(metadata.get("Key Events", []))
        story_outline = json.dumps(metadata.get("Story Outline", {}))
        special_instructions = metadata.get("Special Instructions", "")
        result = (
            self.supabase.table("stories")
            .insert(
                {
                    "title": metadata.get("Title", "Untitled Story"),
                    "setting": setting,
                    "key_events": key_events,
                    "special_instructions": special_instructions,
                    "story_outline": story_outline,
                    "current_episode": 1,
                    "num_episodes": num_episodes,
                }
            )
            .execute()
        )
        story_id = result.data[0]["id"]
        characters = metadata.get("Characters", {})
        for char_name, data in characters.items():
            self.supabase.table("characters").insert(
                {
                    "story_id": story_id,
                    "name": data["Name"],
                    "role": data["Role"],
                    "description": data["Description"],
                    "relationship": json.dumps(data["Relationship"]),
                    "is_active": True,
                }
            ).execute()
        if not result.data:
            raise Exception("Failed to insert story metadata into Supabase")
        return story_id

    def store_episode(self, story_id: int, episode_data: Dict, current_episode: int) -> int:
        """Store an episode and update story metadata."""
        episode_result = (
            self.supabase.table("episodes")
            .upsert(
                {
                    "story_id": story_id,
                    "episode_number": current_episode,
                    "title": episode_data.get("episode_title", f"Episode {current_episode}"),
                    "content": episode_data.get("episode_content", ""),
                    "summary": episode_data.get("episode_summary", ""),
                },
                on_conflict="story_id,episode_number",
            )
            .execute()
        )

        if not episode_result.data:
            raise Exception("Failed to upsert episode into Supabase")

        episode_id = episode_result.data[0]["id"]

        # Handle character_data
        character_data = episode_data.get("characters_featured", {})
        if isinstance(character_data, str):
            try:
                character_data = json.loads(character_data)
            except json.JSONDecodeError:
                character_data = {}

        if not isinstance(character_data, dict):
            character_data = {}

        for char_name, char in character_data.items():
            if not isinstance(char, dict):
                continue
            self.supabase.table("characters").upsert(
                {
                    "story_id": story_id,
                    "name": char.get("Name", char_name),
                    "role": char.get("Role", "supporting"),
                    "description": char.get("Description", ""),
                    "relationship": json.dumps(char.get("Relationship", {})),
                    "is_active": char.get("role_active", True),
                },
                on_conflict="story_id,name",
            ).execute()

        self.supabase.table("stories").update(
            {
                "current_episode": current_episode + 1,
                "setting": json.dumps(episode_data.get("Settings", [])),
                "key_events": json.dumps(episode_data.get("Key Events", [])),
            }
        ).eq("id", story_id).execute()

        return episode_id
