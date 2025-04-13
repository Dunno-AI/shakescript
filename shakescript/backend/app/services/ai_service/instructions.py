from app.services.ai_service.utils import AIUtils
from app.utils import parse_user_prompt
import json
from typing import Dict
import re


class AIInstructions:
    def __init__(self) -> None:
        self.utils = AIUtils()

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
            "Settings": {"Place": "NOT YET INTRODUCED"},
            "Protagonist": [
                {"Name": "string", "Motivation": "string", "Fear": "string"}
            ],
            "Characters": [
                {
                    "Name": "string (Give proper name not examples, only name)",
                    "Role": "string (Protagonist/Antagonist(if any)/others(give roles according to the story))",
                    "Description": "NOT YET INTRODUCED",
                    "Relationship": {"Character_Name": "Relation"},
                    "Emotional_State": "string(initial state)",
                }
            ],
            "Theme": "string",
            "Story Outline": [
                {
                    "Ep X-Y": "Description",
                    "Phase_name": "Exposition/Inciting Incident/Rising Action/Dilemma/Climax/Denouement/Final Episode",
                }
            ],
            "Special Instructions": "string (include tone: e.g., suspenseful)",
        }
        instruction = f"""
        I want your help to write a episodic professional novel/story which would have {num_episodes} episodes.
        This is my Idea for the story:
        <IDEA>
        {cleaned_prompt}
        </IDEA>
        For that I want that you should extract the following data with care.

        - Title: Suggest a title which expresses the feel and theme of the story.
        - Settings: List locations with vivid descriptions as a dictionary (e.g., {{"Cave": "A deep dark cave where the team assembles"}}).
        - Protagonist: Identify the main character with motivation and fears.
        - Characters: All the characters of the story.
        - Theme: Suggest a guiding theme (e.g., redemption).
        - Story Outline: If the story is short, merge phases but include all 6 also maintain the same order of phases as givendont change the order (Exposition, Inciting Incident, Rising Action, Dilemma, Climax, Denouement, Final Episode).
        - Story Outline Description: Give proper outline of the arc also indicate the introduction of characters settings and any supporting characters. 

        IMPORTANT POINTS:
        - There Should be a Proper Begining Which sets the environment for the story and introduces character and
        a proper Ending Arc which concludes the story with a proper ending.
        - Pay special attneion to how the characters are being introduced 
        there must be a logical connection or some past history or events related to the character.
        - Equally and accordingly divide The number of episodes to each phase for a smooth pace of the story.
        - Only give the metadata not any other thing.

        Instructions for each phase:
        <INSTRUCTIONS>
        {json.dumps(self.utils.story_phases, indent = 2)}
        </INSTRUCTIONS>

        Format as JSON:
        {json.dumps(metadata_template, indent=2)}
        """
        response = model.generate_content(instruction)
        raw_text = response.text
        if "```" in raw_text:
            json_pattern = r"(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]
        return json.loads(raw_text)
