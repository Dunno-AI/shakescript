from typing import Dict, List, Any
from app.services.story_service.generation import StoryGeneration
from app.services.story_service.human_validation import HumanValidation
from app.services.story_service.ai_validation import AIValidation
from app.services.story_service.utils import StoryUtils
from app.models.schemas import StoryListItem
from app.services.db_service import DBService
from app.models.schemas import Feedback


class StoryService:
    def __init__(self):
        self.generation = StoryGeneration()
        self.human_validation = HumanValidation()
        self.ai_validation = AIValidation()
        self.utils = StoryUtils()
        self.db_service = self.generation.db_service
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

    def process_episode_batches_with_human_feedback(
        self,
        story_id,
        num_episodes,
        hinglish,
        batch_size,
        feedback: List[Feedback] = [],
    ):
        return self.human_validation.process_episode_batches_with_human_feedback(
            story_id, num_episodes, hinglish, batch_size, feedback
        )

    def process_episode_batches_with_ai_validation(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
    ) -> Dict[str, Any]:
        return self.ai_validation.process_episode_batches_with_ai_validation(
            story_id, num_episodes, hinglish, batch_size
        )

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        return self.utils.update_story_summary(story_id)
