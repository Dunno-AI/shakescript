import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.utils import extract_json_manually
from app.services.embedding_service import EmbeddingService  # For chunks
from typing import Dict, List
import json
import re

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()  # For retrieving chunks

    def extract_metadata(self, user_prompt: str) -> Dict:
        """Extract story metadata from user prompt using Gemini."""
        instruction = """
    Extract structured metadata from the following story prompt and return it as valid JSON.
    - Title: Suggest a concise, pronounceable title (e.g., avoid silent letters or odd spellings).
    - Settings: Identify locations with brief, vivid descriptions and add phonetic pronunciation for each place.
    - Characters: List key entities with roles, descriptions, and phonetic pronunciation for names (e.g., 'Lee-lah' for Lila).
    - Special Instructions: Include a narration tone (e.g., suspenseful, calm) for audio delivery.
    Format EXACTLY as follows:
    {
      "Title": "string",
      "Settings": [{"Place": "string", "Description": "string", "Pronunciation": "string"}],
      "Characters": {
        "Name": {
          "Name": "string",
          "Role": "string",
          "Description": "string",
          "Relationship": {"Character_Name": "Relation"},
          "Pronunciation": "string"
        }
      },
      "Special Instructions": "string (include tone: e.g., suspenseful, cheerful)",
      "Story Outline": {"Episode X-Y (Phase)": "Description"}
    }
    IMPORTANT: Use simple, pronounceable names and terms for TTS compatibility.
        """
        prompt = f"{instruction}\n\nUser Prompt: {user_prompt}"
        response = self.model.generate_content(prompt)
        raw_text = response.text

        if "```json" in raw_text or "```" in raw_text:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return extract_json_manually(raw_text)

    def _parse_episode_response(self, response_text: str, metadata: Dict) -> Dict:
        """Adopted from Colab's Shakyscript.ipynb - lightweight and robust parsing."""
        try:
            episode_data = json.loads(response_text)
            return episode_data
        except json.JSONDecodeError:
            json_pattern = r'```(?:json)?\s*\n(.*?)\n```'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            if matches:
                try:
                    episode_data = json.loads(matches[0])
                    return episode_data
                except:
                    cleaned_text = matches[0].replace("'", "\"")
                    try:
                        episode_data = json.loads(cleaned_text)
                        return episode_data
                    except:
                        pass

            json_pattern2 = r'{[\s\S]*"episode_title"[\s\S]*"episode_content"[\s\S]*}'
            match = re.search(json_pattern2, response_text)
            if match:
                try:
                    cleaned_json = match.group(0).replace("'", "\"")
                    episode_data = json.loads(cleaned_json)
                    return episode_data
                except:
                    pass

            title_match = re.search(r'"episode_title":\s*"([^"]+)"', response_text)
            content_match = re.search(r'"episode_content":\s*"([^"]*(?:(?:"[^"]*)*[^"])*)"', response_text)
            summary_match = re.search(r'"episode_summary":\s*"([^"]+)"', response_text)

            episode_title = title_match.group(1) if title_match else f"Episode {metadata.get('current_episode', 1)}"
            episode_content = content_match.group(1) if content_match else response_text
            episode_summary = summary_match.group(1) if summary_match else "Episode summary not available."

            return {
                "episode_title": episode_title,
                "episode_content": episode_content,
                "episode_summary": episode_summary,  # Included as fallback, but not required in prompt
            }

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict,
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List = None,
    ) -> Dict:
        """Generate episode with chunks, summaries, and minimal character snapshot."""
        settings = metadata.get("Settings", [])
        settings_data = (
            "\n".join(
                f"Place: {s.get('Place', 'Unknown')}, Description: {s.get('Description', 'No description')}"
                for s in settings if isinstance(s, dict)
            )
            or "No settings provided."
        )

        # Last 2 summaries
        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep_num} SUMMARY: {summary}"
                for ep_num, _, summary in prev_episodes
            )
            if prev_episodes
            else ""
        )

        # Top 3 relevant chunks
        query_text = prev_episodes_text if prev_episodes_text else char_text  # Use summaries or char_text as query
        chunks = self.embedding_service.retrieve_relevant_chunks(story_id, query_text, k=3)
        chunks_text = (
            "\n\n".join(
                f"RELEVANT CONTEXT: {chunk['content']}"
                for chunk in chunks
            )
            if chunks
            else ""
        )

        # Minimal character snapshot (name + one-line descriptor for active characters)
        characters = json.loads(char_text) if char_text else {}
        char_snapshot = (
            "\n".join(
                f"{char['Name']}: {char['Description'][:50]}{'...' if len(char['Description']) > 50 else ''}"
                for char in characters.values() if char.get("role_active", True)
            )
            if characters
            else "No active characters yet."
        )

        # Dynamic phase assignment
        intro_threshold = max(1, int(num_episodes * 0.1))
        build_up_threshold = max(1, int(num_episodes * 0.4))
        climax_threshold = max(1, int(num_episodes * 0.8))
        falling_action_threshold = max(1, int(num_episodes * 0.9))
        resolution_threshold = num_episodes

        if num_episodes == 1:
            phase = "ONE-SHOT STORY: Merge all phases into a single episode."
        elif num_episodes == 2:
            phase = "INTRODUCTION & BUILDING ACTION" if episode_number == 1 else "CLIMAX & RESOLUTION"
        elif num_episodes == 3:
            if episode_number == 1:
                phase = "INTRODUCTION"
            elif episode_number == 2:
                phase = "BUILDING ACTION & CLIMAX"
            else:
                phase = "RESOLUTION"
        else:
            if episode_number <= intro_threshold:
                phase = "INTRODUCTION"
            elif episode_number <= build_up_threshold:
                phase = "BUILDING ACTION"
            elif episode_number <= climax_threshold:
                phase = "CLIMAX"
            elif episode_number <= falling_action_threshold:
                phase = "FALLING ACTION"
            else:
                phase = "RESOLUTION"

        instruction = f"""
        You are writing a story titled "{metadata.get('title', 'Untitled Story')}" for audio narration, set in "{settings_data}".
        This is episode {episode_number} out of {num_episodes} (300-400 words).
        
        Guidelines for TTS compatibility:
        - Use short, clear sentences (10-15 words) for easy listening.
        - Make 60-70% of the text dialogue, with emotional cues (e.g., 'shouted angrily', 'whispered softly').
        - Avoid complex phrases, homophones, or dense narration; keep it vivid yet simple.
        - Add natural breaks (e.g., 'She paused.') for audio pacing.
        - End with a cliffhanger or hook to engage listeners.
        - Ensure consistency with previous episodes using the recap, context, and characters below.
        
        Current Phase: {phase}
        Special Instructions: {metadata.get('special_instructions', '')}
        Previous Episodes Recap: {prev_episodes_text}
        Relevant Context (Chunks of previous episodes): {chunks_text}
        Active Characters: {char_snapshot}
        
        Return ONLY valid JSON in this format:
        {{
          "episode_title": "A Short, Pronounceable Title",
          "episode_content": "Dialogue-heavy text with emotional cues and breaks"
        }}
        """
        response = self.model.generate_content(instruction)
        return self._parse_episode_response(response.text, metadata)
