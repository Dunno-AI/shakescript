from supabase import create_client, Client
from app.services.db_service.charactersDB import CharactersDB
from app.core.config import settings
from typing import Dict, List, Any
import json


class EpisodesDB:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )
        self.CharactersDB = CharactersDB()

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

        self.CharactersDB.update_character_state(
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

    def get_episodes_by_range(
        self, story_id: int, start_episode: int, end_episode: int
    ) -> List[Dict[str, Any]]:
        """
        Get episodes for a story within a specific range.
        """
        try:
            result = (
                self.supabase.table("episodes")
                .select("*")
                .eq("story_id", story_id)
                .gte("episode_number", start_episode)
                .lte("episode_number", end_episode)
                .order("episode_number")
                .execute()
            )
            # Check if the response contains data
            if hasattr(result, "data"):
                return result.data
            return []
        except Exception as e:
            print(f"Error fetching episodes: {e}")
            return []

    def get_all_episodes(self, story_id: int) -> List[Dict[str, Any]]:
        """
        Get all stored episodes for a story.
        """
        try:
            result = (
                self.supabase.table("episodes")
                .select("*")
                .eq("story_id", story_id)
                .order("episode_number")
                .execute()
            )
            # Check if the response contains data
            if hasattr(result, "data"):
                return result.data
            return []
        except Exception as e:
            print(f"Error fetching all episodes: {e}")
            return []
