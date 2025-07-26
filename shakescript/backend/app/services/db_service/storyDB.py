# app/services/db_service/storyDB.py

from supabase import Client
from typing import Dict, List, Any
import json
import logging
from datetime import datetime, timezone, timedelta


def _safe_json_loads(json_string: str, default_type: Any = None):
    # ... (this helper function remains the same)
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

    # ... (all other methods like get_all_stories, get_story_info, etc. are correct) ...
    def get_all_stories(self, auth_id: str) -> List[Dict[str, Any]]:
        result = (
            self.client.table("stories")
            .select("id, title, genre, is_completed")
            .eq("auth_id", auth_id)
            .execute()
        )
        return result.data if result.data else []

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
                    "setting": json.dumps(metadata.get("Setting", {})),
                    "key_events": json.dumps([]),
                    "timeline": json.dumps([]),
                    "special_instructions": metadata.get("Special Instructions", ""),
                    "story_outline": json.dumps(metadata.get("Story Outline", [])),
                    "current_episode": 1,
                    "num_episodes": num_episodes,
                    "current_episodes_content": json.dumps([]),
                    "auth_id": auth_id,
                    "genre": metadata.get("Genre", "NULL"),
                    "refinement_method": refinement_method,
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

    def check_and_update_episode_limits(self, auth_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        user_res = (
            self.client.table("users")
            .select("episodes_timestamps, episodes_month_count, month_start_date")
            .eq("auth_id", auth_id)
            .single()
            .execute()
        )
        if not user_res.data:
            return {"error": "User not found."}

        user = user_res.data
        timestamps = user.get("episodes_timestamps") or []
        month_count = user.get("episodes_month_count") or 0
        month_start_date_str = user.get("month_start_date")

        if month_start_date_str:
            month_start_date = datetime.fromisoformat(month_start_date_str).date()
            if now.year > month_start_date.year or now.month > month_start_date.month:
                month_count = 0
                month_start_date_str = now.date().isoformat()
        else:
            month_start_date_str = now.date().isoformat()

        if month_count >= 30:
            return {"error": "Monthly episode limit (30) reached."}

        one_day_ago = now - timedelta(days=1)
        recent_timestamps = [
            t
            for t in timestamps
            if datetime.fromisoformat(t.replace("Z", "+00:00")) > one_day_ago
        ]

        if len(recent_timestamps) >= 15:
            return {"error": "Daily episode limit (15 in 24 hours) reached."}

        new_timestamps = recent_timestamps + [now.isoformat()]

        update_res = (
            self.client.table("users")
            .update(
                {
                    "episodes_timestamps": new_timestamps,
                    "episodes_month_count": month_count + 1,
                    "month_start_date": month_start_date_str,
                }
            )
            .eq("auth_id", auth_id)
            .execute()
        )

        if not update_res.data:
            return {"error": "Failed to update user limits."}

        return {"status": "success"}

    def get_user_profile(self, auth_id: str) -> Dict:
        result = (
            self.client.table("users")
            .select("id, auth_id, name, email, avatar_url, is_premium, created_at")
            .eq("auth_id", auth_id)
            .limit(1)
            .single()
            .execute()
        )
        if not result.data:
            return {"error": "User profile not found."}
        return result.data

    def get_user_stats(self, auth_id: str, created_at: datetime) -> Dict:
        # Fetch stories and user data in parallel for efficiency
        stories_res = (
            self.client.table("stories")
            .select("id, is_completed, genre", count="exact")
            .eq("auth_id", auth_id)
            .execute()
        )
        user_res = (
            self.client.table("users")
            .select("episodes_timestamps, episodes_month_count")
            .eq("auth_id", auth_id)
            .single()
            .execute()
        )

        total_stories = stories_res.count or 0

        # Calculate daily and monthly counts from the user's data
        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(days=1)

        timestamps = (
            user_res.data.get("episodes_timestamps", []) if user_res.data else []
        )
        episodes_day_count = len(
            [
                t
                for t in timestamps
                if datetime.fromisoformat(t.replace("Z", "+00:00")) > one_day_ago
            ]
        )
        episodes_month_count = (
            user_res.data.get("episodes_month_count", 0) if user_res.data else 0
        )

        # Calculate other stats
        completed_stories = (
            sum(1 for story in stories_res.data if story["is_completed"])
            if stories_res.data
            else 0
        )
        in_progress_stories = total_stories - completed_stories
        account_age_days = (now - created_at).days

        return {
            "total_stories": total_stories,
            "total_episodes": episodes_month_count,
            "episodes_day_count": episodes_day_count,
            "episodes_month_count": episodes_month_count,
            "completed_stories": completed_stories,
            "in_progress_stories": in_progress_stories,
            "account_age_days": account_age_days,
            "last_active": now,
        }

    def get_recent_stories(self, auth_id: str, limit: int = 5) -> List[Dict]:
        result = (
            self.client.table("stories")
            .select("id, title, summary, genre, created_at")
            .eq("auth_id", auth_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data if result.data else []
