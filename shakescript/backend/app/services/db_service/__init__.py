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
    def get_all_stories(self):
        return self.stories.get_all_stories()

    def get_story_info(self, story_id: int):
        return self.stories.get_story_info(story_id)

    def store_story_metadata(self, metadata, num_episodes):
        return self.stories.store_story_metadata(metadata, num_episodes)

    def update_story_current_episodes_content(self, story_id, episodes):
        return self.stories.update_story_current_episodes_content(story_id, episodes)

    def get_refined_episodes(self, story_id):
        return self.stories.get_refined_episodes(story_id)

    def clear_current_episodes_content(self, story_id):
        return self.stories.clear_current_episodes_content(story_id)

    def delete_story(self, story_id):
        return self.stories.delete_story(story_id)

    def set_story_completed(self, story_id, completed=True):
        return self.stories.set_story_completed(story_id, completed)

    # Episodes
    def store_episode(self, story_id, episode_data, current_episode):
        return self.episodes.store_episode(story_id, episode_data, current_episode)

    def get_previous_episodes(self, story_id, current_episode, limit=3):
        return self.episodes.get_previous_episodes(story_id, current_episode, limit)

    def get_all_episodes(self, story_id):
        return self.episodes.get_all_episodes(story_id)

    def get_episodes_by_range(self, story_id, start_episode, end_episode):
        return self.episodes.get_episodes_by_range(story_id, start_episode, end_episode)

    # Characters
    def update_character_state(self, story_id, character_data):
        return self.characters.update_character_state(story_id, character_data)
