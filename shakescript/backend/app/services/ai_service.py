import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.utils import parse_user_prompt, parse_episode_response
from app.services.embedding_service import EmbeddingService
from typing import Dict, List
import json
import re


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name= "gemini-2.0-flash", generation_config={"response_mime_type": "application/json"},)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()
        self.current_arc = 0
        self.current_arc_summary = ""
        self.story_phases = {
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
            """,
            "Rising Action": """
            - Escalate obstacles testing the protagonist’s values and skills.  
            - Deepen character bonds or conflicts through shared challenges.  
            - Reveal backstory and complications for characters.  
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
            - Start the final struggle/battle.
            """,
            "Denouement": """
            - Resolve all conflicts with emotional and narrative closure.  
            - Properly End The final struggle.
            - Show consequences of the climax for characters and world.  
            - Reflect growth and themes via dialogue, imagery, or realization.  
            """,
            "Final Episode": """
            - Conclude the journey with a definitive settling of the world and characters’ lives.  
            - Depict the protagonist actively shaping their future, cementing their growth.  
            - End with a poignant, grounded moment—dialogue, action, or imagery—that echoes the story’s heart and leaves no ambiguity.
            """
        }

    def extract_metadata( self, user_prompt: str, num_episodes: int, hinglish: bool = False ) -> Dict:
        cleaned_prompt = parse_user_prompt(user_prompt)
        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun’s fear')"
            if hinglish
            else ""
        )
        metadata_template = {
            "Title": "Suggest a title which expresses the feel and theme of the story (string)",
            "Settings": {"Place": "Description of the place"},
            "Characters": [
                {
                    "Name": "string (Give proper name not examples, only name)",
                    "Role": "string (Protagonist/Antagonist(if any)/others(give roles according to the story))",
                    "Relationship": {"Character_Name": "Relation"},
                    "Description": "string",
                    "Emotional_State": "string(initial state)",
                }
            ],
            "Story Outline": [{"Episode X-Y (Arc-Name)": "Description", "Phase_name": "Exposition/Inciting Incident/Rising Action/Dilemma/Climax/Denouement/Final Episode", },],
        }

        instruction = f"""
        {hinglish_instruction}
        Extract metadata from User Prompt for a {num_episodes}-episode story:
        - Settings: List locations with vivid descriptions as a dictionary (e.g., {{"Cave": "A deep dark cave where the team assembles"}}).
        - Characters: List the all characters including protagonists Give Names properly (eg. Dont do "A group of freinds", Do "Ravi", "Pratyush" differently).
        - Story Outline: eg.(
            For a Short Story:
            [{ {"Episode 1-2 (Whispers in the Fog)": "Description", "Phase_name": "Exposition"} },
             { {"Episode 3 (Mystical Found)": "Description", "Phase_name":"Rising Action/Climax"} },
             { {"Episode 4 (The End)": "Description", "Phase_name":"Denouement/Final Episode"} }]

            For a Long Story:
            [{{"Episode 1-5 (Whispers in Fog)": "Description", "Phase_name": "Exposition"}},
             {{"Episode 6-9 (The Forgotten Map)": "Description", "Phase_name": "Inciting Incident"}},
             {{"Episode 10-16 (Echoes Below)": "Description", "Phase_name": "Rising Action"}},
             {{"Episode 17-20 (Mystical Found)": "Description", "Phase_name": "Rising Action"}},
             {{"Episode 21-24 (Is that him)": "Description", "Phase_name": "Dilemma"}},
             {{"Episode 25-28 (The Grand War)": "Description", "Phase_name": "Climax"}},
             {{"Episode 29 (Light Through Fog)": "Description", "Phase_name": "Denouement"}},
             {{"Episode 30 (Back to normality)": "Description", "Phase_name": "Final Episode"}}]
        ) This is just an example of the format, you can change the number of arcs and their phases. 
          Information of what a particular phase means is given to you use that and give phases accordingly. 
        
        Instruction for each phase:
        {json.dumps(self.story_phases, indent = 2)}

        IMPORTANT POINTS:
        - There Should be a Proper Begining Which sets the environment for the story and introduces character and
        a proper Ending Arc which concludes the story with a proper ending.
        - Pay special attneion to how the characters are being introduced 
        there must be a logical connection or some past history or events related to the character.
        - Equally and accordingly divide The number of episodes to each phase for a smooth pace of the story.

        Format as JSON:
        {json.dumps(metadata_template, indent=2)}
        User Prompt: {cleaned_prompt}
        """
        response = self.model.generate_content(instruction)
        raw_text = response.text

        return json.loads(raw_text)

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
        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun’s fear')"
            if hinglish
            else ""
        )
        settings_data = (
            "\n".join(
                f"{place}: {description}"
                for place, description in metadata.get("setting", {}).items()
            )
            or "No settings provided. Build your own."
        )

        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep['episode_number']}\nTITLE: {ep['title']}\nCONTENT: {ep['content']}\nEMOTIONAL STATE: {ep.get('emotional_state', 'neutral')}"
                for ep in prev_episodes[-2:]
            )
            or "First Episode"
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

        story_outline = metadata.get("story_outline", [])
        episode_info = current_phase = ""
        start = end = 1
        next_arc_info = next_arc_phase = ""
        for i, arc in enumerate(story_outline):
            arc_key = list(arc.keys())[0]
            start, *rest = map(int, arc_key.split(" ")[1].split("-"))
            end = rest[0] if rest else start
            if start <= episode_number <= end:
                if i != self.current_arc:
                    self.current_arc = i
                    self.current_arc_summary = ""
                episode_info = arc[arc_key]
                current_phase = arc.get("Phase_name", "Unknown Phase")
                if i + 1 < len(story_outline):
                    next_arc = story_outline[i + 1]
                    next_arc_key = list(next_arc.keys())[0]
                    next_arc_info = next_arc[next_arc_key]
                    next_arc_phase = next_arc.get("Phase_name", "Unknown Phase")
                break

        chunks_text = (
            "\n\n".join(
                f"RELEVANT CONTEXT: {chunk['content']}"
                for chunk in self.embedding_service.retrieve_relevant_chunks(
                    story_id, f"Structure of current Arc: {episode_info} Current Phase: {current_phase}", k=5
                )
            )
            or ""
        )

        phase_description = ""
        for phase in ["Exposition", "Inciting Incident", "Rising Action", "Dilemma", "Climax", "Denouement"]:
            if phase in current_phase:
                phase_description += self.story_phases[phase] + "\n"

        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" (Not more than 450 words) designed for engaging narration.
        {hinglish_instruction} 
        Set in "{settings_data}"
        ---
        EPISODE POSITION: {episode_number}/{num_episodes}

        CONTEXT:
        Previous 2 Episodes: {prev_episodes_text}
        Relevant Context: {chunks_text}
        Active Characters: {char_snapshot}
        {key_events_summary}

        Current phase of the story is: {current_phase}
        Instructions of current phase:
        {phase_description}

        Arc Episode Number: {episode_number - start}
        Episodes Left in this Arc(including this ep): {end - episode_number + 1}
        Arc Description to follow: {episode_info}
        Arc Summary Till Now: {self.current_arc_summary}
        Next Arc Description: {next_arc_info}
        Next Arc Phase: {next_arc_phase}
        
        The Goal is to create an episode of the story and complete the requirements of this arc in the number of episodes remaining in this arc.
        You also know what has happened in the arc so far using the arc summary given.
        Use the incstructions of this phase to create this episode making it consistent with the previous episodes which you are given already
        and consistent with the next episodes.
        If this arc is about to end keep in mind the Next Arc and its phase so the transition would be smooth.
        
        Common Points to remember regardless of the phase:
        - Logically Explain the abscence of the characters (if any).
        - Pay special attention to introduction of new place or a new character or any change in role or relationship of the character.
          This Introduction should be backed by either giving an history about that or by connecting it meaningfully to the story.
        - Also pay attnetion to supporting characters so the story feels complete.
        - Maintain the Pace just like in previous episodes dont make it too fast.
        - Use varied sentence structures and natural dialogue
        - Emphasize on character emotional journeys also use the episodes emotional state given. 
        - Dont use repetetive phrases from the context given.
        - Output STRICTLY a valid JSON object with NO additional text:
        
        {{
          "episode_title": "Create a unique title (4-5 words) that captures this episode's essence",
          "episode_content": "An immersive episode with compelling storytelling.",
        }}
        """
        
        first_response = self.model.generate_content(instruction)
        first_raw_text = first_response.text

        title_content_data = parse_episode_response(first_raw_text, metadata)
        episode_title = title_content_data.get("episode_title")
        episode_content = title_content_data.get("episode_content")

        details_instruction = f"""
        Based on the following episode title and content, generate additional episode details:

        Title: {episode_title}
        Content: {episode_content}
        Settings: {settings_data}
        Previous Arc Summary: {self.current_arc_summary}
        
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
          "Settings": {{"Place": "Description of the place"}},
          "updated_arc_summary": "A concise 50-70 word summary of the arc till this episode."
        }}
        """
        
        second_response = self.model.generate_content(details_instruction)
        second_raw_text = second_response.text
        
        details_data = json.loads(second_raw_text)
        self.current_arc_summary = details_data.get("updated_arc_summary", self.current_arc_summary)
        
        complete_episode = {
            "episode_title": episode_title,
            "episode_content": episode_content,
            **details_data
        }

        return complete_episode
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
