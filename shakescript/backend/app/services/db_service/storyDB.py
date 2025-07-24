from supabase import Client
from typing import Dict, List, Any
import json
import logging


# --- HELPER FUNCTION ---
# Safely parse JSON strings, returning a default type if the input is None, empty, or invalid.
def _safe_json_loads(json_string: str, default_type: Any = None):
    if json_string is None:
        return default_type() if callable(default_type) else default_type
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        logging.warning(
            f"Could not decode JSON string: {json_string}, returning default."
        )
        return default_type() if callable(default_type) else default_type


class StoryDB:
    def __init__(self, client: Client):
        self.client = client

    def get_all_stories(self, auth_id: str) -> List[Dict[str, Any]]:
        result = (
            self.client.table("stories")
            .select("id, title, genre, is_completed")
            .eq("auth_id", auth_id)
            .execute()
        )
        return result.data if result.data else []

    # --- UPDATED METHOD ---
    def get_story_info(self, story_id: int, auth_id: str) -> Dict:
        story_result = (
            self.client.table("stories")
            .select("*")
            .eq("id", story_id)
            .eq("auth_id", auth_id)
            .execute()
        )
        if not story_result.data:
            return {"error": "Story not found or you do not have access."}

        story_row = story_result.data[0]

        # --- FIX: Parse JSON strings into Python objects ---
        story_row["setting"] = _safe_json_loads(story_row.get("setting"), dict)
        story_row["protagonist"] = _safe_json_loads(story_row.get("protagonist"), list)
        story_row["story_outline"] = _safe_json_loads(
            story_row.get("story_outline"), list
        )
        story_row["timeline"] = _safe_json_loads(story_row.get("timeline"), list)
        story_row["key_events"] = _safe_json_loads(story_row.get("key_events"), list)
        story_row["current_episodes_content"] = _safe_json_loads(
            story_row.get("current_episodes_content"), list
        )
        story_row["refinement_method"] = story_row["refinement_method"]

        episodes_result = (
            self.client.table("episodes")
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
                "key_events": _safe_json_loads(ep.get("key_events"), list),
            }
            for ep in episodes_result.data
        ]

        characters_result = (
            self.client.table("characters")
            .select("*")
            .eq("story_id", story_id)
            .execute()
        )
        characters = [
            {
                "Name": char["name"],
                "Role": char["role"],
                "Description": char["description"],
                "Relationship": _safe_json_loads(char.get("relationship"), dict),
                "role_active": char.get("is_active", True),
                "Emotional_State": char.get("emotional_state", "neutral"),
                "Milestones": _safe_json_loads(char.get("milestones"), list),
            }
            for char in characters_result.data
        ]

        story_row["episodes"] = episodes_list
        story_row["characters"] = characters
        return story_row

    def store_story_metadata(
        self, metadata: Dict, num_episodes: int, refinement_method: str, auth_id: str
    ) -> int:
        result = (
            self.client.table("stories")
            .insert(
                {
                    "title": metadata.get("Title", "Untitled Story"),
                    "protagonist": json.dumps(metadata.get("Protagonist", [])),
                    "setting": json.dumps(
                        metadata.get("Setting", {})
                    ),  
                    "key_events": json.dumps([]),
                    "timeline": json.dumps([]),
                    "special_instructions": metadata.get("Special Instructions", ""),
                    "story_outline": json.dumps(metadata.get("Story Outline", [])),
                    "current_episode": 1,
                    "num_episodes": num_episodes,
                    "current_episodes_content": json.dumps([]),
                    "auth_id": auth_id,
                    "genre": metadata.get("Genre", "NULL"),
                    "refinement_method": refinement_method
                }
            )
            .execute()
        )
        if not result.data:
            raise Exception("Failed to store story metadata")

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
                "auth_id": auth_id,
            }
            for char in metadata.get("Characters", [])
        ]
        if character_data_list:
            self.client.table("characters").insert(character_data_list).execute()
        return story_id

    def update_story_current_episodes_content(
        self, story_id: int, episodes: List[Dict], auth_id: str
    ):
        self.client.table("stories").update(
            {"current_episodes_content": json.dumps(episodes)}
        ).eq("id", story_id).eq("auth_id", auth_id).execute()

    def get_refined_episodes(self, story_id: int, auth_id: str) -> List[Dict]:
        story_data = self.get_story_info(story_id, auth_id)
        # It's already parsed now, so this will work correctly
        return story_data.get("current_episodes_content", [])

    def clear_current_episodes_content(self, story_id: int, auth_id: str):
        self.client.table("stories").update(
            {"current_episodes_content": json.dumps([])}
        ).eq("id", story_id).eq("auth_id", auth_id).execute()

    def delete_story(self, story_id: int, auth_id: str) -> None:
        story = (
            self.client.table("stories")
            .select("id")
            .eq("id", story_id)
            .eq("auth_id", auth_id)
            .execute()
        )
        if not story.data:
            raise ValueError(f"Story with ID {story_id} not found")

        self.client.table("characters").delete().eq("story_id", story_id).execute()
        self.client.table("episodes").delete().eq("story_id", story_id).execute()
        self.client.table("chunks").delete().eq("story_id", story_id).execute()
        self.client.table("stories").delete().eq("id", story_id).execute()

    def set_story_completed(self, story_id: int, completed: bool):
        self.client.table("stories").update({"is_completed": completed}).eq(
            "id", story_id
        ).execute()
