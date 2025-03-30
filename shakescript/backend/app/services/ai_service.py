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

    def extract_metadata(self, user_prompt: str, hinglish: bool = False) -> Dict:
        """Extract story metadata from user prompt using Gemini."""
        cleaned_prompt = parse_user_prompt(user_prompt)
        hinglish_instruction = ""
        if hinglish:
            hinglish_instruction = """
            convert the prompt in hinglish and then create metadata in higlish like for example
            metadata bhi hinglish me nikalna 
            Title: Suggest the story title in HINGLISH language , for example : 
            Title : ek kala ghoda 
            Characters: character ke naam bhi hinglish me likho
            for example : Ram , mohan etc 
            role : bhai , dost etc ..
            settings : settings bhi hinglish me hi honi chahiye 
            """
        metadata_template = {
            "Title": "string",
            "Settings": [
                {"Place": "string", "Description": "string", "Pronunciation": "string"}
            ],
            "Characters": {
                "Name": {
                    "Name": "string",
                    "Role": "string",
                    "Description": "string",
                    "Relationship": {"Character_Name": "Relation"},
                    "Pronunciation": "string",
                }
            },
            "Special Instructions": "string (include tone: e.g., suspenseful, cheerful)",
            "Story Outline": {"Episode X-Y (Phase)": "Description"},
        }
        metadata_template_str = json.dumps(metadata_template, indent=2)
        instruction = f"""
        {hinglish_instruction}
        Extract structured metadata from the following story prompt and return it as valid JSON.
        - Title: Suggest a concise, pronounceable title (e.g., avoid silent letters or odd spellings).
        - Settings: Identify locations with brief, vivid descriptions and add phonetic pronunciation for each place.
        - Characters: List key entities with roles, descriptions, and phonetic pronunciation for names (e.g., 'Lee-lah' for Lila).
        - Special Instructions: Include a narration tone (e.g., suspenseful, calm) for audio delivery.
        Format EXACTLY as follows:
        {metadata_template_str}
        IMPORTANT: Use simple, pronounceable names and terms for TTS compatibility.
        """
        prompt = f"{instruction}\n\nUser Prompt: {cleaned_prompt}"
        response = self.model.generate_content(prompt)
        raw_text = response.text
        if "```" in raw_text:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return extract_json_manually(raw_text)

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
        """Generate a structured and well-curated episode with clear progression from intro to conclusion."""
        settings_data = (
            "\n".join(
                f"Place: {s.get('Place', 'Unknown')}, Description: {s.get('Description', 'No description')}"
                for s in metadata.get("Settings", [])
            )
            or "No settings provided."
        )
        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep_num} SUMMARY: {summary}\nEPISODE {ep_num} CONTENT: {content}"
                for ep_num, content, summary in prev_episodes[-3:]
            )
            if prev_episodes
            else ""
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
                f"{char['Name']}: {char['Description'][:50]}{'...' if len(char['Description']) > 50 else ''}"
                for char in characters.values()
                if char.get("role_active", True)
            )
            or "No active characters yet."
        )

        # Add key events from metadata
        key_events = metadata.get("key_events", [])
        key_events_summary = (
            "Key Story Events So Far: " + "; ".join(key_events)
            if key_events
            else "No key events yet."
        )

        if num_episodes == 1:
            phase = "ONE-SHOT STORY: Merge all phases into a single episode."
        elif episode_number == num_episodes:
            phase = """
            FINAL RESOLUTION:
            - This is the LAST episode. ALL conflicts MUST be resolved.
            - Ensure that all character arcs conclude definitively (success, failure, sacrifice, or transformation).
            - No cliffhangers. No unresolved mysteries.
            - The main antagonist must be defeated, neutralized, or fully resolved.
            - Any prophecy, curse, or mystery must be answered fully.
            - The ending should feel final (happy, tragic, or bittersweet), with a lasting impact.
            """
        elif episode_number == num_episodes - 1:
            phase = "FALLING ACTION: Wrapping up loose threads, preparing for final resolution."
        elif episode_number == 1:
            phase = "INTRODUCTION: Establish setting, introduce main characters, and present initial conflict."
        elif episode_number <= num_episodes * 0.4:
            phase = "BUILDING ACTION: Develop subplots, introduce obstacles, and raise stakes."
        elif episode_number <= num_episodes * 0.8:
            phase = "CLIMAX: Key confrontations occur, major events shift the direction of the story."
        else:
            phase = "BUILDING ACTION"

        hinglish_instruction = ""
        if hinglish:
            hinglish_instruction = """
            generate whole episode in hinglish and return output in same language for example
            episode title: isko bhi hinglish me likhna jaise ( ek chalak lombdi)
            episode content : pura episode hinglish me dena 
            episode summary : ye bhi hinglish me hi generate krna 
            dhyaan se krna ye sb shi shi 
            niche ke saare rule bhi maan na...
            """

        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" designed for engaging narration.
        {hinglish_instruction} Episode {episode_number} of {num_episodes} (Target: 300-400 words).  
        Set in "{settings_data}", this episode must maintain a gripping flow, with a clear beginning, middle, and end.
        ---
        Storytelling Rules for a Stronger Narrative:
        1. Deep Story Consistency & Character Growth:  
           - Maintain logical progression from previous episodes.  
           - Ensure consistent character arcs (strengths, weaknesses, motivations).  
           - Make every action meaningful—no filler dialogue or unnecessary exposition.  
        2. Stronger Narrative Phases for Engagement:  
           Phase: {phase}  
           - Introduction (Ep 1): Establish the world, key characters, and initial mystery.  
           - Rising Action (Ep 2 - {int(num_episodes * 0.4)}): Increase stakes through unexpected challenges.  
           - Climax (Ep {int(num_episodes * 0.5)} - {int(num_episodes * 0.8)}): Major confrontations, twists, and revelations.  
           - Falling Action (Ep {num_episodes - 1}): Start resolving subplots, prepare for the conclusion.  
           - Final Resolution (Ep {num_episodes}): All conflicts MUST be resolved (no cliffhangers).  
        3. Enhance Immersion & Atmosphere:  
           - Use vivid sensory details to immerse the reader (sounds, textures, emotions).  
           - Increase psychological tension through character thoughts, shifting environments, and mind games.  
           - Every episode should advance the overall mystery & deepen the stakes.  
        4. Diverse Threats & Challenges:  
           Avoid repetitive encounters. Integrate:  
           - Physical Threats: Shadows, monsters, environmental hazards.  
           - Psychological Horror: Unreliable memories, illusions, betrayals.  
           - Emotional Conflict: Character-driven tension, moral dilemmas, inner fears.  
        ---
        Your Task: Generate a Well-Paced Episode
        1. Use prior episodes & context below to ensure coherence.  
        2. Prioritize character-driven storytelling & emotional depth.  
        3. Weave in foreshadowing for upcoming twists.  
        Previous Episodes Recap:  
        {prev_episodes_text}  
        Relevant Context (Extracted from Past Episodes):  
        {chunks_text}  
        Active Characters & Their Current Motivations:  
        {char_snapshot}  
        {key_events_summary}
        Output ONLY a valid JSON response in this format:  
        {{
          "episode_title": "A Short, Pronounceable Title",
          "episode_content": "A well-structured, immersive episode with compelling storytelling.",
          "episode_summary": "A concise 50-70 word summary of the episode's key events and outcomes.",
          "characters_featured": {{"Name": {{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true}}}},
          "Key Events": ["Key event 1", "Key event 2"]
        }}
        """
        response = self.model.generate_content(instruction)
        raw_text = response.text
        # print("raw text from ai service............\n", raw_text)
        response_data = self._parse_episode_response(raw_text, metadata)
        # print("response data from _parse_episode_response............\n", response_data)
        return response_data
