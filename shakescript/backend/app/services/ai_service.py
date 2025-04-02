import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.utils import extract_json_manually, parse_user_prompt
from app.services.embedding_service import EmbeddingService
from typing import Dict, List
import json
import re


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()

    def extract_metadata(
        self, user_prompt: str, num_episodes: int, hinglish: bool = False
    ) -> Dict:
        cleaned_prompt = parse_user_prompt(user_prompt)
        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun’s fear')"
            if hinglish
            else ""
        )
        metadata_template = {
            "Title": "string",
            "Settings": {"Place": "Description of the place"},
            "Protagonist": [
                {"Name": "string", "Motivation": "string", "Fear": "string"}
            ],
            "Characters": [
                {
                    "Name": "string (Give proper name not examples, only name)",
                    "Role": "string (Protagonist/Antagonist(if any)/others(give roles according to the story))",
                    "Description": "string",
                    "Relationship": {"Character_Name": "Relation"},
                    "Emotional_State": "string(initial state)",
                }
            ],
            "Theme": "string",
            "Story Outline": {
                "Ep X - Y (Phase_name-Exposition/Inciting Incident/Rising Action/Dilemma/Climax/Denouement)": "Description"
            },
            "Special Instructions": "string (include tone: e.g., suspenseful)",
        }
        instruction = f"""
        {hinglish_instruction}
        Extract metadata from User Prompt for a {num_episodes}-episode story:
        - Title: Suggest a title which expresses the feel and theme of the story.
        - Settings: List locations with vivid descriptions as a dictionary (e.g., {{"Cave": "A deep dark cave where the team assembles"}}).
        - Protagonist: Identify the main character with motivation and fears.
        - Characters: All the characters of the story.
        - Theme: Suggest a guiding theme (e.g., redemption).
        - Story Outline: If the story is short, merge phases but include all 6 (Exposition, Inciting Incident, Rising Action, Dilemma, Climax, Denouement).
        
        IMPORTANT POINTS:
        - The story must have a clear beginning, middle, and satisfiable end.
        - If short, maintain pace and flow, shortening middle phases.
        - If long, make each phase descriptive, engaging, and thrilling.
        Format as JSON:
        {json.dumps(metadata_template, indent=2)}
        User Prompt: {cleaned_prompt}
        """
        response = self.model.generate_content(instruction)
        raw_text = response.text

        if "```" in raw_text:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]
        return json.loads(raw_text)

    def _parse_episode_response(self, response_text: str, metadata: Dict) -> Dict:
        try:
            episode_data = json.loads(response_text)
            return episode_data
        except json.JSONDecodeError:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            if matches:
                try:
                    episode_data = json.loads(matches[0])
                    return episode_data
                except:
                    cleaned_text = matches[0].replace("'", '"')
                    try:
                        episode_data = json.loads(cleaned_text)
                        return episode_data
                    except:
                        pass
            json_pattern2 = r'{[\s\S]*"episode_title"[\s\S]*"episode_content"[\s\S]*}'
            match = re.search(json_pattern2, response_text)
            if match:
                try:
                    cleaned_json = match.group(0).replace("'", '"')
                    episode_data = json.loads(cleaned_json)
                    return episode_data
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
            }

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict,
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List = None,
        hinglish: bool = False,
    ) -> Dict:
        settings_data = (
            "\n".join(
                f"{place}: {description}"
                for place, description in metadata.get(
                    "setting", {}
                ).items()  # Use "setting" consistently
            )
            or "No settings provided. Build your own."
        )

        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep['episode_number']}\nCONTENT: {ep['content']}\nTITLE: {ep['title']}"
                for ep in prev_episodes[-3:]
            )
            or "First Episode"
        )

        chunks_text = (
            "\n\n".join(
                f"RELEVANT CONTEXT: {chunk['content']}"
                for chunk in self.embedding_service.retrieve_relevant_chunks(
                    story_id, prev_episodes_text or char_text, k=5
                )
            )
            or ""
        )
        characters = json.loads(char_text) if char_text else {}
        char_snapshot = (
            "\n".join(
                f"Name: {char.get('Name')}, Role: {char.get('Role', 'Unknown')}, "
                f"Description: {char.get('Description', 'No description available')}, "
                f"Relationships: {json.dumps(char.get('Relationship', {}))}, "
                f"Active: {'Yes' if char.get('role_active', True) else 'No'}, "
                f"Emotional State: {char.get('Emotional_State', 'Unknown')}"
                for char in characters
            )
            or "No characters introduced yet."
        )

        key_events = metadata.get("key_events", [])
        key_events_summary = (
            "Key Story Events So Far: " + "; ".join(key_events)
            if key_events
            else "No key events yet."
        )

        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun’s fear')"
            if hinglish
            else ""
        )

        # Determine current phase (unchanged)
        if num_episodes <= 3:
            if episode_number == 1:
                phase = "INTRODUCTION + RISING_ACTION"
            else:
                phase = "CLIMAX + RESOLUTION"
        elif num_episodes <= 7:
            if episode_number == 1:
                phase = "INTRODUCTION"
            elif episode_number <= max(2, int(num_episodes * 0.6)):
                phase = "RISING_ACTION"
            elif episode_number <= max(4, int(num_episodes * 0.9)):
                phase = "CLIMAX"
            else:
                phase = "RESOLUTION"
        else:
            if episode_number <= 2:
                phase = "INTRODUCTION"
            elif episode_number <= int(num_episodes * 0.2):
                phase = "COMPLICATION"
            elif episode_number <= int(num_episodes * 0.3):
                phase = "FIRST_THRESHOLD"
            elif episode_number <= int(num_episodes * 0.5):
                phase = "PROGRESSIVE_COMPLICATIONS"
            elif episode_number <= int(num_episodes * 0.55):
                phase = "MIDPOINT_REVERSAL"
            elif episode_number <= int(num_episodes * 0.7):
                phase = "TESTING_NEW_PATH"
            elif episode_number <= int(num_episodes * 0.8):
                phase = "CRISIS"
            elif episode_number <= int(num_episodes * 0.9):
                phase = "CLIMAX"
            else:
                phase = "RESOLUTION"

        phase_requirements = {  # Unchanged, keeping it concise
            "INTRODUCTION + RISING_ACTION": "Merge introduction and rising action smoothly for short story.",
            "CLIMAX + RESOLUTION": "Merge climax and resolution smoothly for short story.",
            "INTRODUCTION": "Set world, introduce protagonist, hint at conflict with sensory details.",
            "RISING_ACTION": "Escalate obstacles, deepen character ties, end with a cliffhanger.",
            "COMPLICATION": "Introduce complex challenges, reveal character values.",
            "FIRST_THRESHOLD": "Point of no return, raise stakes, transform protagonist.",
            "PROGRESSIVE_COMPLICATIONS": "Escalate challenges, test limits, add subplots.",
            "MIDPOINT_REVERSAL": "Dramatic shift, recontextualize story, expose truths.",
            "TESTING_NEW_PATH": "Adapt to new path, test growth, build to crisis.",
            "CRISIS": "Darkest moment, impossible choices, reveal strengths.",
            "CLIMAX": "Peak tension, resolve conflicts, show transformation.",
            "RESOLUTION": "Close conflicts, show new status quo, emotional payoff.",
        }

        story_structure = f"{num_episodes} EPISODE STORY: {'SHORT' if num_episodes <= 7 else 'LONG'} FORM - CURRENT PHASE: {phase}"
        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" designed for engaging narration.
        {hinglish_instruction} Episode {episode_number} of {num_episodes} (Target: 300-400 words).
        Set in "{settings_data}", this episode must maintain a gripping flow, with a clear beginning, middle, and end.
        ---
        {story_structure}
        PHASE REQUIREMENTS: {phase_requirements[phase]}

        GUIDELINES:
        - Maintain ALL characters introduced unless explicitly killed or retired. Reference {char_snapshot} for status.
        - If a character is absent, note why (e.g., "Rohan is away searching for clues").
        - Start with a tie-in to the previous episode unless Episode 1.
        - End with a lead-in to the next episode unless final.
        - Ensure logical scene transitions with cause-and-effect.
        - Feature relevant characters with distinct traits.
        - Reveal character depth through challenges.
        - Create sensory-rich descriptions.
        - Use varied sentences and dialogue tags.
        - Fit phase {phase}.

        Your Task: Generate a Well-Paced Episode
        1. Use prior episodes & context for coherence.
        2. Create a unique title (4-5 words) differing from previous ones.
        3. Prioritize character-driven storytelling & emotional depth.
        4. Fulfill the current narrative phase.

        Previous Episodes Recap: {prev_episodes_text}
        Relevant Context: {chunks_text}
        Active Characters & Motivations: {char_snapshot}
        {key_events_summary}

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_title": "A descriptive, Pronounceable Title Representing the Episode",
          "episode_content": "An immersive episode with compelling storytelling.",
        }}
        """
        
        # First model call
        first_response = self.model.generate_content(instruction)
        first_raw_text = first_response.text
        
        # Clean up response text and handle JSON parsing errors
        first_raw_text = first_raw_text.strip()
        # Remove any leading/trailing text often added by LLMs
        if first_raw_text.startswith("```json"):
            first_raw_text = first_raw_text.split("```json", 1)[1]
        if "```" in first_raw_text:
            first_raw_text = first_raw_text.split("```", 1)[0]
        
        try:
            title_content_data = json.loads(first_raw_text)
        except json.JSONDecodeError as e:
            # Fallback to avoid crashing
            title_content_data = {
                "episode_title": "Episode Title Placeholder",
                "episode_content": "Episode content placeholder due to formatting error."
            }
        
        episode_title = title_content_data.get("episode_title")
        episode_content = title_content_data.get("episode_content")

        # Second model call - Generate the rest using the title and content
        details_instruction = f"""
        Based on the following episode title and content, generate additional episode details:

        Title: {episode_title}
        Content: {episode_content}
        
        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_summary": "A concise 50-70 word summary of the episode's key events and outcomes.",
          "episode_emotional_state": "string",
          "characters_featured": [{{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true, "Emotional_State": "string"}}],
          "Key Events": ["Key event 1", "Key event 2"],
          "Settings": {{"Place": "Description of the place"}}
        }}
        """
        
        # Second model call
        second_response = self.model.generate_content(details_instruction)
        second_raw_text = second_response.text
        
        # Clean up second response and handle JSON parsing errors
        second_raw_text = second_raw_text.strip()
        if second_raw_text.startswith("```json"):
            second_raw_text = second_raw_text.split("```json", 1)[1]
        if "```" in second_raw_text:
            second_raw_text = second_raw_text.split("```", 1)[0]
        
        try:
            details_data = json.loads(second_raw_text)
        except json.JSONDecodeError as e:
            details_data = {
                "episode_summary": "Summary placeholder due to formatting error.",
                "episode_emotional_state": "neutral",
                "characters_featured": [],
                "Key Events": [],
                "Settings": {}
            }
        
        # Combine both responses into a complete episode object
        complete_episode = {
            "episode_title": episode_title,
            "episode_content": episode_content,
            **details_data
        }

        return self._parse_episode_response(json.dumps(complete_episode), metadata)

        # ✅ **Call OpenAI's GPT-4o API using self.openai_client**

        # response = self.openai_client.chat.completions.create(
        # model="gpt-4o",
        # messages=[
        # {"role": "system", "content": "You are a professional storyteller creating structured, well-paced narratives."},
        # {"role": "user", "content": instruction}
        # ],
        # temperature=0.7,
        # max_tokens=1000
        # )

        # raw_text = response.choices.message.content or ""
        # return self._parse_episode_response(raw_text, metadata)
