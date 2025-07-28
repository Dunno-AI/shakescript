# app/services/db_service/episodesDB.py

from supabase import Client
from app.services.db_service.charactersDB import CharactersDB
from typing import Dict, List, Any
import json


class EpisodesDB:
    def __init__(self, client: Client):
        """
        KEY CHANGE: Accept the authenticated client.
        """
        self.client = client
        self.CharactersDB = CharactersDB(client)

    def store_episode(
        self, story_id: int, episode_data: Dict, current_episode: int, auth_id: str
    ) -> int:
        episode_result = (
            self.client.table("episodes")
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
                    "auth_id": auth_id,
                },
                on_conflict="story_id,episode_number",
            )
            .execute()
        )
        if not episode_result.data:
            raise Exception(f"Failed to store episode {current_episode}")
        episode_id = episode_result.data[0]["id"]

        self.CharactersDB.update_character_state(
            story_id, episode_data.get("characters_featured", []), auth_id
        )

        story_data_res = (
            self.client.table("stories")
            .select("key_events, setting, timeline")
            .eq("id", story_id)
            .eq("auth_id", auth_id)
            .execute()
        )
        if not story_data_res.data:
            raise Exception("Failed to retrieve story data for update")
        story_data = story_data_res.data[0]

        current_key_events = json.loads(story_data.get("key_events", "[]") or "[]")
        current_timeline = json.loads(story_data.get("timeline", "[]") or "[]")
        new_key_events = [
            event["event"]
            for event in episode_data.get("Key Events", [])
            if event.get("tier") in ["foundational", "character-defining"]
        ]
        new_timeline = [
            {
                "event": e["event"],
                "episode": current_episode,
                "resolved": e.get("tier") in ["foundational", "character-defining"],
            }
            for e in episode_data.get("Key Events", [])
        ]
        self.client.table("stories").update(
            {
                "current_episode": current_episode + 1,
                "setting": json.dumps(
                    {
                        **json.loads(story_data.get("setting", "{}") or "{}"),
                        **episode_data.get("Settings", {}),
                    }
                ),
                "key_events": json.dumps(
                    list(set(current_key_events + new_key_events))
                ),
                "timeline": json.dumps(current_timeline + new_timeline),
            }
        ).eq("id", story_id).eq("auth_id", auth_id).execute()
        return episode_id

    def get_previous_episodes(
        self, story_id: int, current_episode: int, auth_id: str, limit: int = 3
    ) -> List[Dict]:
        result = (
            self.client.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
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
                "key_events": json.loads(ep.get("key_events", "[]") or "[]"),
            }
            for ep in result.data or []
        ]

    def get_episodes_by_range(
        self, story_id: int, start_episode: int, end_episode: int, auth_id: str
    ) -> List[Dict[str, Any]]:
        try:
            result = (
                self.client.table("episodes")
                .select("*")
                .eq("story_id", story_id)
                .eq("auth_id", auth_id)
                .gte("episode_number", start_episode)
                .lte("episode_number", end_episode)
                .order("episode_number")
                .execute()
            )
            return result.data if hasattr(result, "data") else []
        except Exception as e:
            print(f"Error fetching episodes: {e}")
            return []

    def get_all_episodes(self, story_id: int, auth_id: str) -> List[Dict[str, Any]]:
        try:
            result = (
                self.client.table("episodes")
                .select("*")
                .eq("story_id", story_id)
                .eq("auth_id", auth_id)
                .order("episode_number")
                .execute()
            )
            return result.data if hasattr(result, "data") else []
        except Exception as e:
            print(f"Error fetching all episodes: {e}")
            return []
