from app.utils import parse_user_prompt
import json
from typing import Dict
import re


def extract_metadata(
    self, user_prompt: str, num_episodes: int, hinglish: bool, auth_id: str = None
) -> Dict:
    cleaned_prompt = parse_user_prompt(user_prompt)
    metadata_template = {
        "Title": "string",
        "Settings": {"Place": "NOT YET INTRODUCED"},
        "Protagonist": [{"Name": "string", "Motivation": "string", "Fear": "string"}],
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
    instruction = self.prompts.METADATA_EXTRACTOR_PROMPT(
        cleaned_prompt, num_episodes, metadata_template
    )

    response = self.call_llm(instruction, max_tokens=500, temperature=0.7)
    raw_text = response
    if "```" in raw_text:
        json_pattern = r"(?:json)?\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, raw_text, re.DOTALL)
        if matches:
            raw_text = matches[0]
    return json.loads(raw_text)
