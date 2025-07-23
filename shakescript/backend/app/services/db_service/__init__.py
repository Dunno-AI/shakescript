from app.services.db_service.storyDB import StoryDB
from app.services.db_service.episodesDB import EpisodesDB
from app.services.db_service.charactersDB import CharactersDB
from supabase import create_client, Client
from app.core.config import settings

class DBService:
    def __init__(self):
        self.stories = StoryDB()
        self.episodes = EpisodesDB()
        self.characters = CharactersDB()
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    # Stories
    def get_all_stories(self, auth_id: str):
        return self.stories.get_all_stories(auth_id)

    def get_story_info(self, story_id: int, auth_id: str):
        return self.stories.get_story_info(story_id, auth_id)

    def store_story_metadata(self, metadata, num_episodes, auth_id: str):
        return self.stories.store_story_metadata(metadata, num_episodes, auth_id)

    def update_story_current_episodes_content(self, story_id, episodes, auth_id: str):
        return self.stories.update_story_current_episodes_content(story_id, episodes, auth_id)

    def get_refined_episodes(self, story_id, auth_id: str):
        return self.stories.get_refined_episodes(story_id, auth_id)

    def clear_current_episodes_content(self, story_id, auth_id: str):
        return self.stories.clear_current_episodes_content(story_id, auth_id)

    def delete_story(self, story_id, auth_id: str):
        return self.stories.delete_story(story_id, auth_id)

    # Episodes
    def store_episode(self, story_id, episode_data, current_episode, auth_id: str):
        return self.episodes.store_episode(story_id, episode_data, current_episode, auth_id)

    def get_previous_episodes(self, story_id, current_episode, auth_id: str, limit=3):
        return self.episodes.get_previous_episodes(story_id, current_episode, auth_id, limit)

    def get_all_episodes(self, story_id, auth_id: str):
        return self.episodes.get_all_episodes(story_id, auth_id)

    def get_episodes_by_range(self, story_id, start_episode, end_episode, auth_id: str):
        return self.episodes.get_episodes_by_range(story_id, start_episode, end_episode, auth_id)

    # Characters
    def update_character_state(self, story_id, character_data, auth_id: str):
        return self.characters.update_character_state(story_id, character_data, auth_id)
