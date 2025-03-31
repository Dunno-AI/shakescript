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
                {"Place Name": "The Place's Description", "Pronunciation": "string"}
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
        - Settings: Use the format "Place Name": "Description" for each location like ("greenwood":"a dense forest" ).
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
                f"{place}: {description}"
                for place, description in metadata.get("Settings", {}).items()
            )
            or "No settings provided."
        )

        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep_num} SUMMARY: {summary}\nEPISODE {ep_num} CONTENT: {content}\nTITLE:{title}"
                for ep_num, content, summary, title in prev_episodes[-3:]
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

        # Determine current phase
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

        # Phase-specific requirements (focused, compact version)
        phase_requirements = {
            "INTRODUCTION + RISING_ACTION": """
            -This is for short story so you have to merge phases
            -Merge together itroduction and rising action of the story
            -Keep the flow smooth 
            """,
            "CLIMAX + RESOLUTION": """
            -This is for short story so you have to merge phases
            -Merge together climax and resolution of the story
            -Keep the flow smooth 
            """,
            ""
            "INTRODUCTION": """
            -Begin with rich, immersive sensory descriptions (sight, sound, smell, touch, taste) that establish the world
            -Create a distinctive atmosphere through deliberate environmental details and weather patterns
            -Introduce the protagonist through revealing actions, thoughts, and behaviors rather than exposition
            -Establish the character's normal world, routines, and relationships before the inciting incident
            -Subtly hint at underlying tensions or themes that will develop throughout the story
            -Plant seeds of the central conflict without fully revealing it
            -Show the protagonist's strengths, flaws, and desires through specific interactions
            -Create a compelling hook through mystery, tension, or an unexpected event
            -End with a moment that disrupts the status quo and demands a response
            """,
            "RISING_ACTION": """
            -Develop meaningful character conflicts that reveal core values and beliefs
            -Show how supporting characters both help and complicate the protagonist's journey
            -Create a sequence of escalating obstacles that test the protagonist in new ways
            -Deepen emotional connections between characters through shared experiences
            -Reveal backstory elements that contextualize current conflicts and motivations
            -Introduce complications that force characters to make difficult choices
            -Show initial attempts to resolve problems and their consequences
            -Build tension through pacing, dialogue, and environmental pressure
            -End with a mini-cliffhanger that raises stakes and creates urgency
            """,
            "COMPLICATION": """
            -Introduce multi-dimensional obstacles that challenge characters physically, emotionally, and morally
            -Reveal character values through consequential choices and their aftermath
            -Clearly establish world rules, limitations, and consequences for breaking them
            -Create tension between characters with conflicting goals but mutual dependence
            -Develop central conflict through successive revelations and complications
            -Show characters adapting to new information and changing circumstances
            -Introduce secondary characters who represent different approaches to central problems
            -Reveal hidden aspects of familiar settings or relationships
            -Plant elements that will later become crucial plot points
            -Build momentum through increasingly difficult challenges
            """,
            "FIRST_THRESHOLD": """
            -Create a definitive point-of-no-return moment that forces commitment
            -Show characters crossing physical, emotional, or psychological boundaries
            -Force character commitment to the journey through burning bridges or eliminating alternatives
            -Reveal new, unexpected aspects of the world or situation that change perspective
            -Introduce significantly higher stakes that make retreat impossible
            -Firmly establish the narrative path and central conflict
            -Reveal deeper character motivations that explain their willingness to continue
            -Create a moment of transformation or decision that defines the protagonist's journey
            -Challenge character assumptions about their world or situation
            -Show immediate consequences of crossing the threshol
            """,
            "PROGRESSIVE_COMPLICATIONS": """
            -Escalate challenges and stakes in meaningful ways that test character limits
            -Create increasingly difficult obstacles that require new skills or alliances
            -Develop intersecting subplots that complicate the main narrative thread
            -Reveal new character motivations that add complexity to relationships
            -Build tension through complications that force difficult choices
            -Show characters adapting and evolving in response to challenges
            -Create moments of apparent progress followed by setbacks
            -Introduce time pressure or deadline elements that increase urgency
            -Deepen thematic elements through parallel character journeys
            -Challenge character beliefs and assumptions through unexpected developments
            """,
            "MIDPOINT_REVERSAL": """
            -Create a dramatic shift in direction that fundamentally changes the story trajectory
            -Reveal critical information that recontextualizes previous events and choices
            -Force characters to reevaluate goals, methods, and alliances
            -Introduce a surprising twist that challenges character assumptions
            -Set a new trajectory that couldn't have been anticipated earlier
            -Show immediate emotional and practical consequences of the reversal
            -Reveal hidden aspects of characters or their situation
            -Transform the nature of the central conflict or how it must be resolved
            -Create a moment of truth that exposes character flaws or strengths
            -Shift power dynamics between key characters in unexpected ways
            """,
            "TESTING_NEW_PATH": """
            -Show adaptation to new circumstances through specific actions and decisions
            -Test relationships under pressure, revealing their true strength and nature
            -Reveal character growth through actions that would have been impossible earlier
            -Introduce complications that test the new approach or understanding
            -Build toward crisis through escalating challenges to the new path
            -Show both successes and failures that result from character changes
            -Create moments of doubt and recommitment to the journey
            -Develop newfound strengths or abilities through practical application
            -Deepen alliances or create new conflicts based on changing priorities
            -Reveal the consequences of earlier choices that now impact the journey
            """,
            "CRISIS": """
            -Present the darkest moment or apparent defeat that seems insurmountable
            -Force confrontation with deep-seated fears, flaws, or painful truths
            -Create a moment where all seems lost and victory appears impossible
            -Reveal hidden strengths, resources, or allies at a crucial moment
            -Strip away character defenses and coping mechanisms
            -Challenge the character's core beliefs or identity
            -Create impossible choices with significant consequences
            -Show the culmination of character flaws or past mistakes
            -End with a crucial decision point that will determine everything
            -Demonstrate what the character values most through their choices under pressure
            """,
            "CLIMAX": """
            -Create the highest tension point through converging conflicts and stakes
            -Force direct confrontation with the antagonist or central challenge
            -Show characters applying what they've learned throughout their journey
            -Reveal final surprises or twists that recontextualize the struggle
            -Bring primary conflicts to a head in a definitive, high-stakes confrontation
            -Demonstrate character growth through choices different from earlier patterns
            -Create moments of sacrifice that show character transformation
            -Test character resolve through final temptations or doubts
            -Show the resolution of internal and external conflicts
            -Create visual, emotional, and thematic culmination of story elements
            """,
            "RESOLUTION": """
            -Resolve esolve main conflicts with emotional and narrative satisfaction
            -Show the consequences of actions and growth for all key characters
            -Provide meaningful closure to relationships and narrative threads
            -Reflect on thematic elements through character realizations or symbolic moments
            -Leave a memorable final impression through imagery, dialogue, or reflection
            -Show the new status quo and how it differs from the starting point
            -Address how characters have been transformed by their experiences
            -Create emotional payoff for reader investment in character journeys
            -Tie up loose ends while leaving appropriate elements for potential continuation
            -Reinforce the story's central message or question through final moments
            """,
        }

        print("phase", phase)
        # print("phase_requirements", phase_requirements[phase])

        # Compact story structure based on length
        story_structure = f"""
        {num_episodes} EPISODE STORY:
        - {"SHORT" if num_episodes <= 7 else "LONG"} FORM - CURRENT PHASE: {phase}
        """
        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" designed for engaging narration.
        {hinglish_instruction} Episode {episode_number} of {num_episodes} (Target: 300-400 words).  
        Set in "{settings_data}", this episode must maintain a gripping flow, with a clear beginning, middle, and end.
        ---
        {story_structure}
    
        PHASE REQUIREMENTS:
        {phase_requirements[phase]}
        
        GUIDELINES:
        - Feature relevant characters with distinct traits
        - Reveal character depth through challenges
        - Create sensory-rich descriptions
        - Use varied sentences and dialogue tags
        - Ensure this episode fits phase {phase}
        - Always ensure that the flow and transitions are smooth and engaging

        Your Task: Generate a Well-Paced Episode
        1. Use prior episodes & context below to ensure coherence.
        2. Create a unique title (4-5 words) that differs from previous episodes
        3. Prioritize character-driven storytelling & emotional depth.
        4. Ensure this episode fulfills its role in the current narrative phase.

        Previous Episodes Recap:  
        -Title should not be same to previous ones.(it can be upto 4 5 words like murder of the blind lady).
        -Episodes should align properly with the past episodes.
        {prev_episodes_text}  
        Relevant Context (Extracted from Past Episodes):  
        {chunks_text}  
        Active Characters & Their Current Motivations:  
        {char_snapshot}  
        {key_events_summary}
        Output ONLY a valid JSON response in this format:
        Strictly follow this format so that the response can be parsed correctly:
        {{
          "episode_title": "A Short, Pronounceable Title",
          "episode_content": "A well-structured, immersive episode with compelling storytelling.",
          "episode_summary": "A concise 50-70 word summary of the episode's key events and outcomes.",
          "characters_featured": {{"Name": {{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true}}}},
          "Key Events": ["Key event 1", "Key event 2"]
        }}
        """
        # ╭──────────────╮
        # │ gemini model │
        # ╰──────────────╯
        response = self.model.generate_content(instruction)
        raw_text = response.text
        # print("raw text from ai service............\n", raw_text)
        response_data = self._parse_episode_response(raw_text, metadata)
        # print("response data from _parse_episode_response............\n", response_data)
        return response_data

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
