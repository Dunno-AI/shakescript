# app/services/ai_service/__init__.py

import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from .metadata_extractorAI import extract_metadata
from .episode_generatorAI import AIGeneration
from .utilsAI import AIUtils
from .prompts import AIPrompts
from .ai_refinementAI import (
    validate_batch,
    is_consistent_with_previous,
    check_episode_quality,
)
from .human_refinementAI import (
    regenerate_batch,
    generate_episode_title,
)
from app.services.embedding_service import EmbeddingService
from supabase import Client
from typing import Dict, List, Any, Optional


class AIService:
    def __init__(self, client: Client):
        """
        KEY CHANGE: Accepts the authenticated Supabase client and passes
        it to services like EmbeddingService that need it.
        """
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # KEY CHANGE: Pass the client to EmbeddingService during initialization
        self.embedding_service = EmbeddingService(client)
        self.generation = AIGeneration(self.model, self.embedding_service)
        self.utils = AIUtils()
        self.prompts = AIPrompts()
        self.client = client  # Store client for any potential direct use

    def call_llm(
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7
    ) -> str:
        """
        Call the AI model with the given prompt.
        """
        instruction = prompt
        first_response = self.model.generate_content(instruction)
        return first_response.text

    def extract_metadata(
        self,
        user_prompt: str,
        num_episodes: int,
        hinglish: bool = False,
        auth_id: str = None,
    ) -> Dict:
        return extract_metadata(self, user_prompt, num_episodes, hinglish, auth_id)

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict,
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List = [],
        hinglish: bool = False,
        auth_id: str = None,  # Added auth_id
    ) -> Dict:
        return self.generation.generate_episode_helper(
            num_episodes,
            metadata,
            episode_number,
            char_text,
            story_id,
            prev_episodes,
            hinglish,
            auth_id,
        )

    def validate_batch(
        self,
        story_id: int,
        current_episodes: List[Dict],
        prev_episodes: List[Dict],
        metadata: Dict,
        auth_id: str,
    ) -> Dict[str, Any]:
        return validate_batch(
            self, story_id, current_episodes, prev_episodes, metadata, auth_id
        )

    def regenerate_batch(
        self,
        story_id: int,
        current_episodes: List[Dict],
        prev_episodes: List[Dict],
        metadata: Dict,
        feedback: List[Dict],
        auth_id: str,
    ) -> List[Dict]:
        return regenerate_batch(
            self, story_id, current_episodes, prev_episodes, metadata, feedback, auth_id
        )

    def is_consistent_with_previous(
        self, current_episode: Dict, previous_episode: Dict
    ) -> bool:
        return is_consistent_with_previous(self, current_episode, previous_episode)

    def check_episode_quality(self, episode: Dict, metadata: Dict) -> Optional[str]:
        return check_episode_quality(self, episode, metadata)

    def generate_episode_title(self, episode_content: str) -> str:
        return generate_episode_title(self, episode_content)
