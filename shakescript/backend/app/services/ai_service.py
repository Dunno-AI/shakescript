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
            "Story Outline": [{"Episode X-Y": "Description", "Phase_name": "Exposition/Inciting Incident/Rising Action/Dilemma/Climax/Denouement", },],
            "Special Instructions": "string (include tone: e.g., suspenseful)",
        }
        instruction = f"""
        {hinglish_instruction}
        Extract metadata from User Prompt for a {num_episodes}-episode story:
        - Title: Suggest a title which expresses the feel and theme of the story.
        - Settings: List locations with vivid descriptions as a dictionary (e.g., {{"Cave": "A deep dark cave where the team assembles"}}).
        - Protagonist: Identify the main character with motivation and fears.
        - Theme: Suggest a guiding theme (e.g., redemption).
        
        IMPORTANT POINTS:
        - The story must have a clear beginning, middle, and satisfiable end.
        - If short, maintain pace and flow, merge middle phases.
        - If long, make each phase descriptive, engaging, and thrilling.
        - It is important that the story must fit in the number of episodes specified in the user_prompt.
        - Dont give same episode multiple times in the outline merge the phases instead.
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
                for place, description in metadata.get("setting", {}).items()
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

        story_outline = metadata.get("story_outline", [])
        episode_info = current_phase = ""
        start = end = 1
        for arc in story_outline:
            arc_key = list(arc.keys())
            episode_range = arc_key[0].split(" ")[1].split("-")
            
            if len(episode_range) == 2:
                start = int(episode_range[0])
                end = int(episode_range[1])
            else:
                start = end = int(episode_range[0])
                
            if start <= episode_number <= end:
                episode_info = arc[arc_key[0]]
                current_phase = arc.get("Phase_name", "Unknown Phase")
                break
        
        next_phase = {
                "EXPOSITION": "INCITING INCIDENT",
                "INCITING INCIDENT": "RISING ACTION", 
                "RISING ACTION": "DILEMMA", 
                "DILEMMA": "CLIMAX", 
                "CLIMAX": "DENOUEMENT", 
                "DENOUEMENT": "END"
            }.get(current_phase, "UNKNOWN")
        is_phase_start = episode_number == start
        is_phase_end = episode_number == end

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

        story_phases = {
            "Exposition": """
            - Set the scene with vivid sensory details (sight, sound, smell) and atmosphere.  
            - Introduce the protagonist via actions and thoughts, showing their normal world and backstory.  
            - Highlight strengths, flaws, and routines through interactions.  
            - Subtly hint at tensions or themes to come.
            """,
            "Inciting Incident": """
            - Disrupt the status quo with a mysterious, tense, or unexpected event.  
            - Hook with a moment demanding the protagonist’s response.  
            - Plant seeds of the central conflict without full reveal.  
            - Raise stakes to push the story forward.
            """,
            "Rising Action": """
            - Escalate obstacles testing the protagonist’s values and skills.  
            - Deepen character bonds or conflicts through shared challenges.  
            - Reveal backstory and complications forcing tough choices.  
            - Build tension with pacing and a mini-cliffhanger raising stakes.
            """,
            "Dilemma": """
            - Present a multi-layered obstacle (emotional, moral, physical) with no easy solution.  
            - Force a pivotal choice revealing the protagonist’s core beliefs.  
            - Heighten stakes with conflicting goals and mutual reliance.  
            - End with urgency pushing toward a critical decision.
            """,
            "Climax": """
            - Peak tension as conflicts collide in a decisive confrontation.  
            - Force the protagonist to face the central challenge or antagonist.  
            - Reveal a final twist or surprise recontextualizing the struggle.  
            - Show growth through bold choices and sacrifices, testing resolve.
            """,
            "Denouement": """
            - Resolve conflicts with emotional and narrative closure.  
            - Show consequences of the climax for characters and world.  
            - Reflect growth and themes via dialogue, imagery, or realization.  
            - Establish a new status quo, leaving a memorable final impression.
            """
        }

        phase_description = ""
        for phase in ["Exposition", "Inciting Incident", "Rising Action", "Dilemma", "Climax", "Denouement"]:
            if phase in current_phase:
                phase_description += story_phases[phase] + "\n"

        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" (Not more than 450 words) designed for engaging narration.
        {hinglish_instruction} 
        Set in "{settings_data}"
        ---
        EPISODE POSITION: {episode_number}/{num_episodes} - {current_phase} PHASE
        PHASE PROGRESSION: {"START of " + current_phase if is_phase_start else "MIDDLE of " + current_phase if not is_phase_end else "END of " + current_phase}
        In this phase {end - episode_number + 1} episodes remain.

        PHASE CONTEXT:
        {episode_info}

        PHASE REQUIREMENTS:
        {phase_description}

        NARRATIVE CONTINUITY:
        {f"Connect smoothly to previous phase themes and create a clear transition into {current_phase} energy." if is_phase_start else ""}
        {f"Begin transitioning toward {next_phase} while resolving key {current_phase} elements." if is_phase_end and current_phase != "DENOUEMENT" else ""}
        {f"Provide meaningful closure to story arcs and character journeys." if current_phase == "DENOUEMENT" and is_phase_end else ""}
        {f"Deepen and develop core {current_phase} themes and conflicts." if not is_phase_start and not is_phase_end else ""}

        GUIDELINES:
        - If a character is absent, briefly explain why
        - Begin with a clear connection to previous episode unless this is Episode 1
        - Ensure logical scene transitions with clear cause-and-effect
        - Create sensory-rich descriptions that immerse the reader
        - Use varied sentence structures and natural dialogue
        - Balance action, dialogue, and internal reflection
        - Emphasize on character emotional journeys. 
        - Ensure emotional progression reflects phase position. 

        STORYTELLING FOCUS:
        1. Use prior episodes & context for coherence
        2. Create a unique title (4-5 words) that captures this episode's essence

        CONTEXT:
        Previous Episodes: {prev_episodes_text}
        Relevant Context: {chunks_text}
        Active Characters: {char_snapshot}
        {key_events_summary}

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_title": "A descriptive, Title Representing the Episode",
          "episode_content": "An immersive episode with compelling storytelling.",
        }}
        """
        # - Previous episode emotional tone: {prev_episode_emotional_state if episode_number > 1 else "N/A"}
        
        first_response = self.model.generate_content(instruction)
        first_raw_text = first_response.text
        
        first_raw_text = first_raw_text.strip()
        if first_raw_text.startswith("```json"):
            first_raw_text = first_raw_text.split("```json", 1)[1]
        if "```" in first_raw_text:
            first_raw_text = first_raw_text.split("```", 1)[0]
        
        try:
            title_content_data = json.loads(first_raw_text)
        except json.JSONDecodeError as e:
            title_content_data = {
                "episode_title": "Episode Title Placeholder",
                "episode_content": "Episode content placeholder due to formatting error."
            }
        
        episode_title = title_content_data.get("episode_title")
        episode_content = title_content_data.get("episode_content")

        details_instruction = f"""
        Based on the following episode title and content, generate additional episode details:

        Title: {episode_title}
        Content: {episode_content}
        Settings: {settings_data}
        
        - Settings: Any new place in this episode eg., {{"cave": "Place where team assembles"}}
        - episode_emotional_state: The emotional tone of this episode (e.g., happy, sad, neutral)
        - characters_featured: Add new character if any in this episode update previous char relations, emotions, descriptions.
        - Key Events: Key events of this episode(2 to 4).
        
        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_summary": "A concise 50-70 word summary of the episode's key events and outcomes.",
          "episode_emotional_state": "string (the emotional state shown in this episode)",
          "characters_featured": [{{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true, "Emotional_State": "string"}}],
          "Key Events": ["String (Key Events of this episode)"],
          "Settings": {{"Place": "Description of the place"}}
        }}
        """
        
        second_response = self.model.generate_content(details_instruction)
        second_raw_text = second_response.text
        
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
        # {"role": "system", "content": "You are a professional storyteller creating structured, well-paced narratives, maintain consistency between episodes and phase transitions."},
        # {"role": "user", "content": instruction}
        # ],
        # temperature=0.7,
        # max_tokens=1000
        # )
        #
        # raw_text = response.choices[0].message.content or ""
        # return self._parse_episode_response(raw_text, metadata)
