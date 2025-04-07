import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.services.ai_service.instructions import AIInstructions
from app.services.ai_service.generation import AIGeneration
from app.services.ai_service.utils import AIUtils
from app.services.embedding_service import EmbeddingService
from typing import Dict, List
import re , json


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()
        self.instructions = AIInstructions()
        self.generation = AIGeneration(self.model, self.embedding_service)
        self.utils = AIUtils()

    def extract_metadata(
        self, user_prompt: str, num_episodes: int, hinglish: bool = False
    ) -> Dict:
        return self.instructions.extract_metadata(
            user_prompt, num_episodes, hinglish, self.model
        )

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict,
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List = [],
        hinglish: bool = False,
    ) -> Dict:
        return self.generation.generate_episode_helper(
            num_episodes,
            metadata,
            episode_number,
            char_text,
            story_id,
            prev_episodes,
            hinglish,
        )

    def _apply_human_input(self, content: str, human_input: str) -> str:
        return self.utils.apply_human_input(content, human_input)

    # Add these methods to your existing AIService class

    def interpret_feedback(self, feedback: str, episodes: List[Dict]) -> List[Dict]:
        """Use AI to interpret user feedback into structured commands"""
        prompt = f"""
        The user has given feedback on story episodes: "{feedback}"
        
        Based on this feedback, extract the following information:
        1. Which episode number(s) the feedback applies to
        2. What type of change is requested:
           - "title": Change the title to a specific value
           - "ai_title": Generate a better title
           - "line": Replace specific text with new text
           - "improved_line": Improve a specific line with a style
           - "style": Enhance content with a specific style element
           - "content": General content modification
        3. Any specific values provided:
           - For "title": the new_value
           - For "line": the old_text and new_text
           - For "improved_line": the line and style (e.g., "suspenseful", "dramatic", "humorous")
           - For "style": the style name (e.g., "suspense", "humor", "drama", "action")  
           - For "content": the instruction
        
        Return the structured interpretation as a JSON array of changes.
        Example: [
          {{"episode_number": 2, "change_type": "title", "new_value": "The New Title"}},
          {{"episode_number": 1, "change_type": "improved_line", "line": "John walked slowly", "style": "suspenseful"}}
        ]
        
        Available episodes: {[f"Episode {ep['episode_number']}: {ep['episode_title']}" for ep in episodes]}
        """

        response = self._call_ai_model(prompt)

        # Try to parse response into structured format
        try:
            return json.loads(response)
        except:
            # Fallback for when parsing fails - extract episode number if possible
            episode_match = re.search(r"episode\s+(\d+)", feedback, re.IGNORECASE)
            episode_num = int(episode_match.group(1)) if episode_match else 1

            return [
                {
                    "episode_number": episode_num,
                    "change_type": "content",
                    "instruction": feedback,
                }
            ]

    def improve_line(self, original_line, style, context):
        """Generate an improved version of a line with specified style"""
        prompt = f"""
        Original line: "{original_line}"
        
        Please rewrite this line to make it more {style}.
        Consider the surrounding context: 
        "{context[:200]}... [line] ...{context[-200:]}"
        
        Return only the improved line without any explanations.
        """

        return self._call_ai_model(prompt).strip()

    def replace_similar_text_with_improved(self, content, approximate_text, style):
        """Find text similar to the provided text and replace with improved version"""
        prompt = f"""
        Content: "{content}"
        
        The user wants to improve this text that's approximately: "{approximate_text}"
        
        Task:
        1. Find the most similar text in the content
        2. Rewrite that text to make it more {style}
        3. Return the full content with ONLY that specific text replaced
        
        Return the complete modified content.
        """

        return self._call_ai_model(prompt).strip()

    def generate_better_title(
        self, current_title, episode_content, story_context, instruction
    ):
        """Generate an improved title based on feedback"""
        prompt = f"""
        Current title: "{current_title}"
        
        Episode content: "{episode_content[:500]}..."
        
        Story context: 
        Title: {story_context["title"]}
        Setting: {story_context["setting"]}
        
        User instruction: "{instruction}"
        
        Please generate an improved title for this episode.
        Return only the new title without any explanations.
        """

        return self._call_ai_model(prompt).strip()

    def enhance_content_style(self, content, style, story_context):
        """Enhance content with a specific style element"""
        prompt = f"""
        Content: "{content}"
        
        Please enhance this content to include more {style}.
        The story is about: {story_context["title"]} set in {story_context["setting"]}
        
        Return the complete enhanced content.
        """

        return self._call_ai_model(prompt).strip()

    def replace_similar_text(self, content, old_text, new_text):
        """Replace text similar to old_text with new_text"""
        prompt = f"""
        Content: "{content}"
        
        Find text most similar to: "{old_text}"
        Replace it with: "{new_text}"
        
        Return the complete modified content.
        """

        return self._call_ai_model(prompt).strip()

    def _apply_human_input1(self, content, instruction):
        """Apply general human feedback to content"""
        prompt = f"""
        Content: "{content}"
        
        User feedback: "{instruction}"
        
        Please modify the content according to the feedback.
        Return the complete modified content.
        """

        return self._call_ai_model(prompt).strip()

    def _call_ai_model(self, prompt):
        """Make the actual API call to the AI model"""
        return self.model.generate_content(prompt).text
