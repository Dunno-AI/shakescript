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

    def update_character_state(self, story_id: int, character_data: List[Dict]) -> None:
        for char in character_data:
            current_char = (
                self.supabase.table("characters")
                .select("*")
                .eq("story_id", story_id)
                .eq("name", char["Name"])
                .execute()
                .data
            )
            if not current_char:
                continue
            current = current_char[0]
            new_emotional = char.get("Emotional_State", current["emotional_state"])
            milestones = json.loads(current["milestones"] or "[]")
            if new_emotional != current["emotional_state"]:
                milestones.append(
                    {
                        "event": f"Shift to {new_emotional}",
                        "episode": current.get("last_episode", 0) + 1,
                    }
                )
            self.supabase.table("characters").update(
                {
                    "emotional_state": new_emotional,
                    "relationship": json.dumps(
                        {
                            **json.loads(current["relationship"] or "{}"),
                            **char.get("Relationship", {}),
                        }
                    ),
                    "milestones": json.dumps(milestones[-5:]),
                    "last_episode": current.get("last_episode", 0) + 1,
                }
            ).eq("id", current["id"]).execute()

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

        self.update_character_state(
            story_id, episode_data.get("characters_featured", [])
        )

        story_data = (
            self.supabase.table("stories")
            .select("key_events, setting, timeline")
            .eq("id", story_id)
            .execute()
            .data[0]
        )
        current_key_events = json.loads(story_data["key_events"] or "[]")
        current_timeline = json.loads(story_data["timeline"] or "[]")
        new_key_events = [
            event["event"]
            for event in episode_data.get("Key Events", [])
            if event["tier"] in ["foundational", "character-defining"]
        ]
        new_timeline = [
            {
                "event": e["event"],
                "episode": current_episode,
                "resolved": e["tier"] in ["foundational", "character-defining"],
            }
            for e in episode_data.get("Key Events", [])
        ]
        self.supabase.table("stories").update(
            {
                "current_episode": current_episode + 1,
                "setting": json.dumps(
                    {
                        **json.loads(story_data["setting"]),
                        **episode_data.get("Settings", {}),
                    }
                ),
                "key_events": json.dumps(
                    list(set(current_key_events + new_key_events))
                ),
                "timeline": json.dumps(current_timeline + new_timeline),
            }
        ).eq("id", story_id).execute()
        return episode_id

    def get_previous_episodes(
        self, story_id: int, current_episode: int, limit: int = 3
    ) -> List[Dict]:
        result = (
            self.supabase.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .lt("episode_number", current_episode)
            .order("episode_number", desc=True)
            .limit(limit)
            .execute()
        )
        return [
            {
                "episode_number": ep["episode_number"],
                "content": ep["content"],
                "title": ep["title"],
                "emotional_state": ep["emotional_state"],
                "key_events": json.loads(ep["key_events"] or "[]"),
            }
            for ep in result.data or []
        ]
