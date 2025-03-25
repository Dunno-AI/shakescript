import google.generativeai as genai
from app.core.config import settings
from app.utils import extract_json_manually
from typing import Dict, List
import json
import re


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def extract_metadata(self, user_prompt: str) -> Dict:
        """Extract story metadata from user prompt using Gemini."""
        instruction = """
    Extract structured metadata from the following story prompt and return it as valid JSON.
    - Title: Suggest a concise, fitting title based on the prompt.
    - Settings: Identify where the story takes place. Look for locations or places mentioned (e.g., "forest", "Mars") and provide a brief description for each.
    - Characters: Identify key entities (e.g., people, creatures) mentioned in the prompt as characters. Assign roles (main or supporting) and provide brief descriptions. Do not separate main and supporting characters into different categories.
    - Special Instructions: Any specific details or constraints mentioned (e.g., episode count, tone).
    
    Format the response EXACTLY as follows (with these exact keys and structure):
    {
      "Title": "string",
      "Settings": [{"Place": "string", "Description": "string"}],
      "Characters": {
        "Name": {
          "Name": "string",
          "Role": "string" (main or supporting),
          "Description": "string",
          "Relationship": {"Character_Name": "Relation"}
        }
      },
      "Special Instructions": "string",
      "Story Outline": {
        "Episode X-Y (Phase of the story intro/building action/climax/falling action/conclusion only)": "Description"
      }
        }

        IMPORTANT: Return ONLY valid JSON format with no additional text or explanations. Use the number of episodes specified in the prompt to structure the Story Outline.
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
        """Parse episode responses from Gemini."""
        try:
            episode_data = json.loads(response_text)
            return episode_data
        except json.JSONDecodeError:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    cleaned_text = matches[0].replace("'", '"')
                    try:
                        return json.loads(cleaned_text)
                    except:
                        pass

            title_match = re.search(r'"episode_title":\s*"([^"]+)"', response_text)
            content_match = re.search(
                r'"episode_content":\s*"([^"]*(?:(?:"[^"]*)*[^"])*)"', response_text
            )
            summary_match = re.search(r'"episode_summary":\s*"([^"]+)"', response_text)

            episode_title = (
                title_match.group(1)
                if title_match
                else f"Episode {metadata.get('current_episode', 1)}"
            )
            episode_content = content_match.group(1) if content_match else response_text
            episode_summary = (
                summary_match.group(1)
                if summary_match
                else "Episode summary not available."
            )

            return {
                "episode_title": episode_title,
                "episode_content": episode_content,
                "episode_summary": episode_summary,
                "characters_featured": {},
                "Key Events": [],
                "Settings": [],
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
        """Generate an episode based on metadata and context."""
        story_outline = metadata.get("story_outline", {})
        settings = metadata.get("setting", [])
        settings_data = "\n".join(
            f"Place: {s['Place']}, Description: {s['Description']}" for s in settings
        )

        if episode_number == 1:
            episode_info = next(
                (arc for arc in story_outline if "1" in arc or "Episode 1" in arc),
                "Introduction to the world and characters",
            )
            prev_episodes_text = ""
        else:

            def find_episode_arc(episode_number, story_outline):
                for arc in story_outline:
                    match = arc.split(" ")[1]
                    if "-" in match:
                        start, end = map(int, match.split("-"))
                        if start <= episode_number <= end:
                            return arc
                return f"Episode {episode_number}"

            episode_info = find_episode_arc(episode_number, story_outline)
            prev_episodes_text = (
                "\n\n".join(
                    f"EPISODE {ep_num} SUMMARY: {summary}"
                    for ep_num, _, summary in prev_episodes
                )
                if prev_episodes
                else ""
            )

        phase = (
            "INTRODUCTION"
            if "Intro" in episode_info
            else (
                "BUILDING ACTION"
                if "Building" in episode_info
                else "CLIMAX" if "Climax" in episode_info else "CONCLUSION"
            )
        )
        if episode_number == num_episodes:
            phase = "FINAL EPISODE: Resolve all plot points."

        instruction = f"""
        You are writing a story titled "{metadata.get('title', 'Untitled Story')}", set in "{settings_data}".
        This is episode {episode_number} out of {num_episodes} (300-400 words).

        Guidelines:
        - Make each episode unique.
        - Resolve previous hooks.
        - Ensure consistency with previous episodes.

        Current Phase: {phase}
        Key Events: {', '.join(metadata.get('key_events', []))}
        Special Instructions: {metadata.get('special_instructions', '')}
        Previous Episodes Recap: {prev_episodes_text}
        Character Data: {char_text}
        Current Arc: {episode_info}

        JSON Response Format:
        {{
            "episode_title": "A Unique Episode Title",
            "episode_content": "The full text of the episode",
            "episode_summary": "A brief summary (100-150 words)",
            "characters_featured": {{
                "Name": {{
                    "Name": "string",
                    "Role": "string",
                    "Description": "string",
                    "Relationship": {{"Character_Name": "Relation"}},
                    "role_active": true/false
                }}
            }},
            "Key Events": ["List of updated key events"],
            "Settings": [{{"Place": "Description"}}]
        }}
        """
        response = self.model.generate_content(instruction)
        return self._parse_episode_response(response.text, metadata)
