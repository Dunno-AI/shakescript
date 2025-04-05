from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, List, Any
import json


class DBService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    def get_all_stories(self) -> List[Dict[str, Any]]:
        result = self.supabase.table("stories").select("id, title").execute()
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
            .select("id, episode_number, title, content, summary, emotional_state , key_events")
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
                "key_events": json.loads(ep.get("key_events", "[]")),
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
            }
            for char in characters_result.data
        ]

        # Ensure setting is a Dict[str, str]
        setting = json.loads(story_row["setting"] or "{}")
        if not isinstance(setting, dict):
            setting = {}

        protagonist = json.loads(story_row["protagonist"] or "[]")
        if not isinstance(protagonist, list):
            protagonist = []

        story_outline = json.loads(story_row["story_outline"] or "[]")
        if not isinstance(story_outline, list):
            story_outline = []

        # print("\n\nstory_outline..................\n", story_outline)

        return {
            "id": story_row["id"],
            "title": story_row["title"],
            "setting": setting,
            "key_events": json.loads(story_row["key_events"] or "[]"),
            "special_instructions": story_row["special_instructions"],
            "story_outline": story_outline,
            "current_episode": story_row["current_episode"],
            "episodes": episodes_list,
            "characters": characters,
            "summary": story_row.get("summary"),
            "num_episodes": story_row["num_episodes"],
            "protagonist": protagonist,
        }

    def store_story_metadata(self, metadata: Dict, num_episodes: int) -> int:
        setting = json.dumps(metadata.get("Settings", {}))
        story_outline = json.dumps(metadata.get("Story Outline", {}))
        special_instructions = metadata.get("Special Instructions", "")
        protagonist = json.dumps(metadata.get("Protagonist", []))

        result = (
            self.supabase.table("stories")
            .insert(
                {
                    "title": metadata.get("Title", "Untitled Story"),
                    "protagonist": protagonist,
                    "setting": setting,
                    "key_events": json.dumps([]),
                    "special_instructions": special_instructions,
                    "story_outline": story_outline,
                    "current_episode": 1,
                    "num_episodes": num_episodes,
                }
            )
            .execute()
        )

        if not result.data:
            raise Exception("Failed to insert story metadata into Supabase")

        story_id = result.data[0]["id"]
        characters = metadata.get("Characters", [])

        if not isinstance(characters, list):
            characters = []

        character_data_list = [
            {
                "story_id": story_id,
                "name": char["Name"],
                "role": char["Role"],
                "description": char["Description"],
                "relationship": json.dumps(char.get("Relationship", {})),
                "emotional_state": char.get("Emotional_State", "neutral"),
                "is_active": True,
            }
            for char in characters
        ]

        if character_data_list:
            self.supabase.table("characters").insert(character_data_list).execute()

        return story_id

    def update_character_state(self, story_id: int, character_data: List[Dict]) -> None:
        """
        Update character state based on recent emotional changes and relationships
        """
        for char in character_data:
            name = char.get("Name")
            if not name:
                continue

            # Get current character data
            current_char = (
                self.supabase.table("characters")
                .select("*")
                .eq("story_id", story_id)
                .eq("name", name)
                .execute()
            )

            if not current_char.data:
                continue

            current_state = current_char.data[0]

            # Update emotional state and relationships with memory
            new_emotional = char.get(
                "Emotional_State", current_state.get("emotional_state", "neutral")
            )
            new_relationships = char.get("Relationship", {})

            # Remember important emotional shifts
            if new_emotional != current_state.get("emotional_state"):
                emotional_history = json.loads(
                    current_state.get("emotional_history") or "[]"
                )
                emotional_history.append(
                    {
                        "from": current_state.get("emotional_state", "neutral"),
                        "to": new_emotional,
                        "episode": current_state.get("last_episode", 0) + 1,
                    }
                )
                # Keep only significant changes
                if len(emotional_history) > 5:
                    emotional_history = emotional_history[-5:]
            else:
                emotional_history = json.loads(
                    current_state.get("emotional_history") or "[]"
                )

            # Update character
            self.supabase.table("characters").update(
                {
                    "emotional_state": new_emotional,
                    "emotional_history": json.dumps(emotional_history),
                    "relationship": json.dumps(
                        {
                            **json.loads(current_state.get("relationship") or "{}"),
                            **new_relationships,
                        }
                    ),
                    "last_episode": current_state.get("last_episode", 0) + 1,
                }
            ).eq("id", current_state.get("id")).execute()

    def store_episode(
        self, story_id: int, episode_data: Dict, current_episode: int
    ) -> int:
        episode_result = (
            self.supabase.table("episodes")
            .upsert(
                {
                    "story_id": story_id,
                    "episode_number": current_episode,
                    "title": episode_data.get(
                        "episode_title", f"Episode {current_episode}"
                    ),
                    "content": episode_data.get("episode_content", ""),
                    "summary": episode_data.get("episode_summary", ""),
                    "key_events": json.dumps(episode_data.get("Key Events", [])),
                    "emotional_state": episode_data.get(
                        "episode_emotional_state", "neutral"
                    ),
                },
                on_conflict="story_id,episode_number",
            )
            .execute()
        )
        episode_id = episode_result.data[0]["id"]

        character_data = episode_data.get("characters_featured", [])
        self.update_character_state(story_id, character_data)

        story_data = (
            self.supabase.table("stories")
            .select("key_events, setting")
            .eq("id", story_id)
            .execute()
            .data
        )
        current_key_events = (
            json.loads(story_data[0]["key_events"] or "[]") if story_data else []
        )
        current_setting = (
            json.loads(story_data[0]["setting"] or "{}") if story_data else {}
        )

        new_key_events = [
            event["event"]
            for event in episode_data.get("Key Events", [])
            if event["tier"] in ["foundational", "character-defining"]
        ]
        updated_key_events = list(set(current_key_events + new_key_events))
        updated_setting = {**current_setting, **episode_data.get("Settings", {})}

        self.supabase.table("stories").update(
            {
                "current_episode": current_episode + 1,
                "setting": json.dumps(updated_setting),
                "key_events": json.dumps(updated_key_events),
            }
        ).eq("id", story_id).execute()

        return episode_id

    def get_previous_episodes(
        self, story_id: int, current_episode: int, limit: int = 3
    ) -> List[Dict]:
        """
        Fetch the previous episodes for context.
        """
        result = (
            self.supabase.table("episodes")
            .select("episode_number, content,title, emotional_state, key_events")
            .eq("story_id", story_id)
            .lt("episode_number", current_episode)
            .order("episode_number", desc=True)
            .limit(limit)
            .execute()
        )
        return [
            {
                "episode_number": ep["episode_number"],
                "content": ep["episode_content"],
                "title": ep["episode_title"],
                "emotional_state": ep["emotional_state"],
                "key_events": json.loads(ep["key_events"] or "[]"),
            }
            for ep in result.data or []
        ]
