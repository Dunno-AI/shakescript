# app/services/db_service/__init__.py

from .storyDB import StoryDB
from .episodesDB import EpisodesDB
from .charactersDB import CharactersDB
from supabase import Client
from typing import Dict, List, Any
from datetime import datetime, timezone


class DBService:
    def __init__(self, client: Client):
        """
        KEY CHANGE: Accepts an authenticated client and passes it down
        to each specific database service.
        """
        self.client = client  # Store for direct access if needed
        self.stories = StoryDB(client)
        self.episodes = EpisodesDB(client)
        self.characters = CharactersDB(client)

    def get_all_stories(self, auth_id: str):
        return self.stories.get_all_stories(auth_id)

    def get_story_info(self, story_id: int, auth_id: str):
        return self.stories.get_story_info(story_id, auth_id)

    def store_story_metadata(self, metadata, num_episodes, refinement_method, auth_id: str):
        return self.stories.store_story_metadata(metadata, num_episodes,refinement_method, auth_id)

    def update_story_current_episodes_content(self, story_id, episodes, auth_id: str):
        return self.stories.update_story_current_episodes_content(
            story_id, episodes, auth_id
        )

    def get_refined_episodes(self, story_id, auth_id: str):
        return self.stories.get_refined_episodes(story_id, auth_id)

    def clear_current_episodes_content(self, story_id, auth_id: str):
        return self.stories.clear_current_episodes_content(story_id, auth_id)

    def delete_story(self, story_id, auth_id: str):
        return self.stories.delete_story(story_id, auth_id)

    def store_episode(self, story_id, episode_data, current_episode, auth_id: str):
        return self.episodes.store_episode(
            story_id, episode_data, current_episode, auth_id
        )

    def get_previous_episodes(self, story_id, current_episode, auth_id: str, limit=3):
        return self.episodes.get_previous_episodes(
            story_id, current_episode, auth_id, limit
        )

    def get_all_episodes(self, story_id, auth_id: str):
        return self.episodes.get_all_episodes(story_id, auth_id)

    def get_episodes_by_range(self, story_id, start_episode, end_episode, auth_id: str):
        return self.episodes.get_episodes_by_range(
            story_id, start_episode, end_episode, auth_id
        )

    def update_character_state(self, story_id, character_data, auth_id: str):
        return self.characters.update_character_state(story_id, character_data, auth_id)

    def set_story_completed(self, story_id: int, completed: bool):
        self.stories.set_story_completed(story_id, completed)

    def get_user_profile(self, auth_id: str) -> Dict:
        return self.stories.get_user_profile(auth_id)

    def get_user_stats(self, auth_id: str, created_at: datetime) -> Dict:
        return self.stories.get_user_stats(auth_id, created_at)

    def get_recent_stories(self, auth_id: str, limit: int = 5) -> List[Dict]:
        return self.stories.get_recent_stories(auth_id, limit)

    def check_and_update_episode_limits(self, auth_id: str) -> Dict[str, Any]:
        """
        Checks and updates user episode limits by calling the method in StoryDB.
        """
        return self.stories.check_and_update_episode_limits(auth_id)
