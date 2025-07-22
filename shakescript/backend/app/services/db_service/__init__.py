from supabase import create_client, Client
from app.core.config import settings
from typing import List, Dict, Any


class DBService:
    def __init__(self):
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def get_story_info(self, story_id: int, auth_id: str) -> Dict[str, Any]:
        response = (
            self.supabase.table("stories")
            .select("*")
            .eq("id", story_id)
            .eq("auth_id", auth_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return {"error": f"Story {story_id} not found"}

    def get_all_stories(self, auth_id: str) -> List[Dict[str, Any]]:
        response = (
            self.supabase.table("stories").select("*").eq("auth_id", auth_id).execute()
        )
        return response.data or []

    def store_story_metadata(
        self, metadata: Dict[str, Any], num_episodes: int, auth_id: str
    ) -> int:
        data = {
            **metadata,
            "num_episodes": num_episodes,
            "current_episode": 1,
            "auth_id": auth_id,
        }
        response = self.supabase.table("stories").insert(data).execute()
        return response.data[0]["id"] if response.data else -1

    def store_episode(
        self,
        story_id: int,
        episode_data: Dict[str, Any],
        episode_number: int,
        auth_id: str,
    ) -> int:
        data = {
            **episode_data,
            "story_id": story_id,
            "episode_number": episode_number,
            "auth_id": auth_id,
        }
        response = self.supabase.table("episodes").insert(data).execute()
        return response.data[0]["id"] if response.data else -1

    def get_episodes_by_range(
        self, story_id: int, start: int, end: int, auth_id: str
    ) -> List[Dict[str, Any]]:
        response = (
            self.supabase.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
            .filter("episode_number", "gte", start)
            .filter("episode_number", "lte", end)
            .execute()
        )
        return response.data or []

    def get_previous_episodes(
        self, story_id: int, current_episode: int, auth_id: str, limit=3
    ) -> List[Dict[str, Any]]:
        response = (
            self.supabase.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
            .filter("episode_number", "lt", current_episode)
            .order("episode_number", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    def update_story_current_episodes_content(
        self, story_id: int, episodes: List[Dict], auth_id: str
    ):
        self.supabase.table("stories").update(
            {"current_episodes_content": episodes}
        ).eq("id", story_id).eq("auth_id", auth_id).execute()

    def clear_current_episodes_content(self, story_id: int, auth_id: str):
        self.supabase.table("stories").update({"current_episodes_content": None}).eq(
            "id", story_id
        ).eq("auth_id", auth_id).execute()

    def delete_story(self, story_id: int, auth_id: str):
        self.supabase.table("episodes").delete().eq("story_id", story_id).eq(
            "auth_id", auth_id
        ).execute()
        self.supabase.table("stories").delete().eq("id", story_id).eq(
            "auth_id", auth_id
        ).execute()

    def get_refined_episodes(self, story_id: int, auth_id: str) -> List[Dict]:
        response = (
            self.supabase.table("episodes")
            .select("*")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
            .filter("status", "eq", "refined")
            .execute()
        )
        return response.data or []
