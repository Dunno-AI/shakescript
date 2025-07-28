from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from supabase import Client

class UsersDB:
    def __init__(self, client: Client):
        self.client = client

    def check_and_update_episode_limits(self, auth_id: str) -> Dict[str, Any]:
        """Check daily/monthly episode limits and update counters"""
        now = datetime.now(timezone.utc)

        # Single fetch for user limit data
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

        # Reset month if a new month started
        if month_start_date_str:
            month_start_date = datetime.fromisoformat(month_start_date_str).date()
            if now.year > month_start_date.year or now.month > month_start_date.month:
                month_count = 0
                month_start_date_str = now.date().isoformat()
        else:
            month_start_date_str = now.date().isoformat()

        # Check limits
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

        # Update user counters
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
        """Fetch minimal user profile info"""
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
        """Return story + episode stats + account age"""
        # Fetch stories + user in parallel calls
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

        # Compute episode counts
        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(days=1)
        timestamps = user_res.data.get("episodes_timestamps", []) if user_res.data else []

        episodes_day_count = len(
            [t for t in timestamps if datetime.fromisoformat(t.replace("Z", "+00:00")) > one_day_ago]
        )
        episodes_month_count = user_res.data.get("episodes_month_count", 0) if user_res.data else 0

        # Compute story stats
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
