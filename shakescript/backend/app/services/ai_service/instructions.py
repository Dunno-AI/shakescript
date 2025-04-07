from app.utils import parse_user_prompt
import json
from typing import Dict
import re


class AIInstructions:
    def extract_metadata(
        self, user_prompt: str, num_episodes: int, hinglish: bool, model
    ) -> Dict:
        cleaned_prompt = parse_user_prompt(user_prompt)
        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun's fear')"
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
            "Story Outline": [
                {
                    "Ep X-Y": "Description",
                    "Phase_name": "Exposition/Inciting Incident/Rising Action/Dilemma/Climax/Denouement",
                }
            ],
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
        response = model.generate_content(instruction)
        raw_text = response.text
        if "```" in raw_text:
            json_pattern = r"(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]
        return json.loads(raw_text)
