from typing import Dict, List, Any
from app.models.schemas import Feedback, StoryListItem
from app.services.db_service import DBService
from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService
from app.services.core_service import (
    ai_refinement_core,
    human_refinement_core,
    utils_core,
    story_generator_core,
)
from app.services.core_service.refinement_generation_core import (
    generate_and_refine_batch,
)


class StoryService:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()
        self.DEFAULT_BATCH_SIZE = 2

    async def create_story(
        self,
        prompt: str,
        num_episodes: int,
        hinglish: bool = False,
        auth_id: str = None,
    ) -> Dict[str, Any]:
        return await story_generator_core.create_story(
            self, prompt, num_episodes, hinglish, auth_id
        )

    def get_story_info(self, story_id: int, auth_id: str) -> Dict[str, Any]:
        return utils_core.get_story_info(self, story_id, auth_id)

    def get_all_stories(self, auth_id: str) -> List[StoryListItem]:
        return utils_core.get_all_stories(self, auth_id)

    def generate_multiple_episodes(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
        auth_id: str = None,
    ) -> List[Dict[str, Any]]:
        return story_generator_core.generate_multiple_episodes(
            self, story_id, num_episodes, hinglish, batch_size, auth_id
        )

    def update_story_summary(self, story_id: int, auth_id: str) -> Dict[str, Any]:
        return utils_core.update_story_summary(self, story_id, auth_id)

    def store_validated_episodes(
        self, story_id: int, episodes: List[Dict[str, Any]], auth_id: str
    ) -> None:
        return utils_core.store_validated_episodes(self, story_id, episodes, auth_id)

    def generate_and_refine_batch(
        self,
        story_id: int,
        batch_size: int,
        hinglish: bool,
        refinement_type: str,
        auth_id: str,
    ):
        return generate_and_refine_batch(
            self, story_id, batch_size, hinglish, refinement_type, auth_id
        )

    def update_current_episodes_content(
        self, story_id: int, episodes: List[Dict], auth_id: str
    ):
        self.db_service.update_story_current_episodes_content(
            story_id, episodes, auth_id
        )

    def get_refined_episodes(self, story_id: int, auth_id: str) -> List[Dict]:
        # Get any refined episodes that haven't been validated yet
        return self.db_service.get_refined_episodes(story_id, auth_id)

    def clear_current_episodes_content(self, story_id: int, auth_id: str):
        # Clear the current episodes after they've been validated and stored
        self.db_service.clear_current_episodes_content(story_id, auth_id)

    def delete_story(self, story_id: int, auth_id: str) -> None:
        self.db_service.delete_story(story_id, auth_id)

    def refine_episode_batch(
        self, story_id: int, feedback: List[Feedback], auth_id: str
    ):
        return human_refinement_core.refine_episode_batch(
            self, story_id, feedback, auth_id
        )

    def validate_episode_batch(self, story_id: int, auth_id: str):
        return human_refinement_core.validate_episode_batch(self, story_id, auth_id)

    def refine_batch_by_ai(
        self,
        story_id,
        episodes,
        prev_episodes,
        metadata,
        story_data,
        current_episode,
        batch_size,
        refinement_type,
        hinglish,
        auth_id: str,
    ):
        return ai_refinement_core.refine_batch_by_ai(
            self,
            story_id,
            episodes,
            prev_episodes,
            metadata,
            story_data,
            current_episode,
            batch_size,
            refinement_type,
            hinglish,
            auth_id,
        )

    def set_story_completed(self, story_id: int, completed: bool = True):
        return self.db_service.set_story_completed(story_id, completed)
