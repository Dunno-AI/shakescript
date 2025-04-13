from typing import Dict, List, Any
from app.services.story_service.generation import StoryGeneration
from app.services.story_service.storage import store_validated_episodes
from app.services.story_service.refinement import generate_and_refine_batch
from app.services.story_service.utils import StoryUtils
from app.models.schemas import StoryListItem, Feedback
from app.services.db_service import DBService
from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService


class StoryService:
    def __init__(self):
        self.ai_service = AIService()
        self.generation = StoryGeneration()
        self.utils = StoryUtils()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()
        self.DEFAULT_BATCH_SIZE = 2

    async def create_story(
        self, prompt: str, num_episodes: int, hinglish: bool = False
    ) -> Dict[str, Any]:
        return await self.generation.create_story(prompt, num_episodes, hinglish)

    def get_story_info(self, story_id: int) -> Dict[str, Any]:
        return self.utils.get_story_info(story_id)

    def get_all_stories(self) -> List[StoryListItem]:
        return self.utils.get_all_stories()

    def generate_episode(
        self,
        story_id: int,
        episode_number: int,
        num_episodes: int,
        hinglish: bool = False,
        prev_episodes: List = [],
    ) -> Dict[str, Any]:
        return self.generation.generate_episode(
            story_id, episode_number, num_episodes, hinglish, prev_episodes
        )

    def generate_and_store_episode(
        self,
        story_id: int,
        episode_number: int,
        num_episodes: int,
        hinglish: bool = False,
        prev_episodes: List = [],
    ) -> Dict[str, Any]:
        return self.generation.generate_and_store_episode(
            story_id, episode_number, num_episodes, hinglish, prev_episodes
        )

    def generate_multiple_episodes(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
    ) -> List[Dict[str, Any]]:
        return self.generation.generate_multiple_episodes(
            story_id, num_episodes, hinglish, batch_size
        )

    def get_episodes_by_range(
        self, story_id: int, start_episode: int, end_episode: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve episodes for a story within a specific range.
        """
        return self.generation.get_episodes_by_range(
            story_id, start_episode, end_episode
        )

    def get_all_episodes(self, story_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all episodes for a story.
        """
        return self.generation.get_all_episodes(story_id)

    # def process_episode_batches_with_human_feedback(
    # self,
    # story_id: int,
    # num_episodes: int,
    # hinglish: bool = False,
    # batch_size: int = 1,
    # feedback: List[Feedback] = [],
    # ) -> Dict[str, Any]:
    # return self.human_validation.process_episode_batches_with_human_feedback(
    # story_id, num_episodes, hinglish, batch_size, feedback
    # )

    # def process_episode_batches_with_ai_validation(
    # self,
    # story_id: int,
    # num_episodes: int,
    # hinglish: bool = False,
    # batch_size: int = 1,
    # ) -> Dict[str, Any]:
    # return self.ai_validation.process_episode_batches_with_ai_validation(
    # story_id, num_episodes, hinglish, batch_size
    # )

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        return self.utils.update_story_summary(story_id)

    def store_validated_episodes(
        self, story_id: int, episodes: List[Dict[str, Any]]
    ) -> None:
        return store_validated_episodes(self, story_id, episodes)

    def generate_and_refine_batch(
        self, story_id: int, batch_size: int, hinglish: bool, refinement_type: str
    ):
        return generate_and_refine_batch(
            self, story_id, batch_size, hinglish, refinement_type
        )

    def update_current_episodes_content(self, story_id: int, episodes: List[Dict]):
        self.db_service.update_story_current_episodes_content(story_id, episodes)

    def get_refined_episodes(self, story_id: int) -> List[Dict]:
        # Get any refined episodes that haven't been validated yet
        return self.db_service.get_refined_episodes(story_id)

    def clear_current_episodes_content(self, story_id: int):
        # Clear the current episodes after they've been validated and stored
        self.db_service.clear_current_episodes_content(story_id)
