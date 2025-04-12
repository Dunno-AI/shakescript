import json
import re
from typing import Dict, List, Any, Optional
from app.services.ai_service.utils import AIUtils
from app.services.embedding_service import EmbeddingService


class AIGeneration:
    def __init__(self, model, embedding_service: EmbeddingService):
        self.model = model
        self.embedding_service = embedding_service
        self.utils = AIUtils()

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict[str, Any],
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List[Dict[str, Any]] = [],
        hinglish: bool = False,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        settings_data = (
            "\n".join(
                f"{place}: {description}"
                for place, description in metadata.get("setting", {}).items()
            )
            or "No settings provided. Build your own."
        )

        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep.get('episode_number', 'N/A')}\nCONTENT: {ep.get('content', 'No content')}\nTITLE: {ep.get('title', 'No title')}"
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
        
        try:
            characters = json.loads(char_text) if char_text else []
            if not isinstance(characters, list):
                characters = []
        except json.JSONDecodeError:
            characters = []

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
        episode_info = current_phase = next_phase = ""
        start = end = num_episodes
        for i, arc in enumerate(story_outline):
            arc_key = list(arc.keys())[0]
            episode_range = arc_key.split(" ")[1].split("-")
            start, end = (
                (int(episode_range[0]), int(episode_range[1]))
                if len(episode_range) == 2
                else (int(episode_range[0]), int(episode_range[0]))
            )
            if start <= episode_number <= end:
                episode_info = arc[arc_key]
                current_phase = arc.get("Phase_name", "Unknown Phase")
                if i + 1 < len(story_outline):
                    next_phase = story_outline[i + 1].get("Phase_name", "Unknown Phase")
                break

        transition_guide = f"""
        This is the last episode of this phase So we have to smoothly transit to the next phase:
        {(
            self._get_phase_transition_guide(current_phase, next_phase)
            if next_phase
            else ""
        )}"""
        phase_description = f"""Things you can follow in this phase:
        {self._get_phase_description(current_phase)}"""

        PHASE_INFORMATION = ( transition_guide if end == episode_number and next_phase != current_phase else phase_description)
        key_events_summary = self._summarize_key_events(
            metadata.get("key_events", []), characters, episode_info
        )

        general_pts = """
        GENERAL POINTS:
        - Use Character Snapshot to track arcs and relationships, but shift focus to secondary characters or subplots at least once per episode.
        - When ever introduce a new character, show their backstory and introduce their role in the story.
        - Whenever remove a character, show their departure and the impact on the story properly.
        - Use sensory-rich descriptions and varied dialogue, alternating tone (e.g., tense, reflective, humorous) to keep the style dynamic.
        - Are you skipping days at a time? Summarizing events? Don't do that, add scenes to detail them.
        - Is the story rushing over certain plot points and excessively focusing on others?
        - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
        - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?
        - Characters: Who are the characters in this chapter? What do they mean to each other? What is the situation between them? Is it a conflict? Is there tension? Is there a reason that the characters have been brought together?
        - Development: What are the goals of each character, and do they meet those goals? Do the characters change and exhibit growth? Do the goals of each character change over the story?
        - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
        - Dialogue: Does the dialogue make sense? Is it appropriate given the situation? Does the pacing make sense for the scene E.g: (Is it fast-paced because they're running, or slow-paced because they're having a romantic dinner)? 
        - Disruptions: If the flow of dialogue is disrupted, what is the reason for that disruption? Is it a sense of urgency? What is causing the disruption? How does it affect the dialogue moving forwards? 
        - Fill the episodes with necessary details.

        Don't answer these questions directly, instead make your plot implicitly answer them. (Show, don't tell)
        """

        feedback_pts = """
        You have to refine this Episode based on the feedback given below.
        FEEDBACK:
        {feedback}

        From the Previous Episode Recaps understand what this episode was about and based on the FEEDBACK refine this Episode.
        
        - Does the Episode fits in the story where it belongs?
        - Does the requirements of the feedback are fullfilled?
        - Does the episode feels fresh and not use anything from the previous episodes?

        Don't answer these questions directly, instead make your plot implicitly answer them. (Show, don't tell)
        """

        GENERATE_OR_REFINE = (
            general_pts if not feedback else general_pts + "\n" + feedback_pts
        )

        instruction = f"""
        I want your help in crafting the story titled "{metadata.get('title', 'Untitled Story')}" for engaging narration.
        We will now be generating the EPISODE {episode_number} of {num_episodes} (Target: upto 450 words).
        The story is set in diverse environments inspired by 
        <SETTINGS>
        {settings_data}
        </SETTINGS>

        Avoid repetitive weather references (e.g., rain) unless critical to the plot. Vary the opening line with actions, dialogue, or unexpected events instead of fixed patterns.

        ---
        CURRENT_PHASE: {current_phase}
        Brief of things that should happen in this phase: {episode_info}
        <PHASE_INFORMATION>
        {PHASE_INFORMATION}
        </PHASE_INFORMATION>

        {GENERATE_OR_REFINE} 

        <Previous_Episodes (use sparingly to avoid over-reliance)> 
        {prev_episodes_text}
        </Previous_Episodes>
        <Relevant_Context (integrate creatively, not as a template)>
        {chunks_text}
        </Relevant_Context>
        <Character_Snapshot>
        {char_snapshot}
        </Character_Snapshot>
        <Key_Events>
        {key_events_summary}
        </Key_Events>

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_title": "A descriptive, Pronounceable Title",
          "episode_content": "An immersive episode with compelling storytelling and varied style."
        }}
        """
        if feedback:
            instruction += f"\nStrictly follow this : Apply the following REFINEMENT based on feedback:\n{feedback}"

        first_response = self.model.generate_content(instruction)
        title_content_data = self.utils._parse_episode_response(first_response.text, metadata)
        if hinglish:
            title_content_data = self.hinglish_conversion(title_content_data["episode_content"], title_content_data["episode_title"])

        details_instruction = f"""
        I have written episode {episode_number} for the story "{metadata.get('title', 'Untitled Story')}".
        Title: 
        {title_content_data['episode_title']}
        Content: 
        {title_content_data['episode_content']}

        GUIDELINES:
        - Update all the asked details extract enough information so that I can write the next episode by just reading these.
        - Update Character Snapshot based on content (emotional state, relationships).
        - Identify 1-3 Key Events; tag as 'foundational' if they shift the story significantly, 'character-defining' if they develop a character.
        - Summarize concisely (50-70 words) with vivid language.
        - Assign emotional state reflecting tone.

        Character Snapshot: {char_snapshot}
        Relevant Context: {chunks_text}

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_summary": "string",
          "episode_emotional_state": "string",
          "characters_featured": [{{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true, "Emotional_State": "string"}}],
          "Key Events": [{{"event": "string", "tier": "foundational/character-defining/transitional/contextual"}}],
          "Settings": {{"Place": "Description"}}
        }}
        """
        second_response = self.model.generate_content(details_instruction)
        details_data = self.utils._parse_and_clean_response(second_response.text, metadata)

        complete_episode = {
            "episode_number": episode_number,
            "episode_title": title_content_data["episode_title"],
            "episode_content": title_content_data["episode_content"],
            **details_data,
        }
        return self.utils._parse_episode_response(json.dumps(complete_episode), metadata)

    def hinglish_conversion(self, ep_content, ep_title)->Dict[str, Any]:
        instruction = f"""
        I want your help in converting one of my story's episode to Hinglish.
        EPISODE TITLE:
        {ep_title}
        EPISODE CONTENT:
        {ep_content}

        GUIDELINES:
        - Convert both the title and episode content to Hinglish.
        - Dont use any english word unless it becomes a necessity.
        - You just have to translate the episode not change it, it should remain the same but in hinglish.
        - Give output in a JSON format dont give any additional text.

        {{
            "episode_title": "string",
            "episode_content": "string",
        }}
        """

        reposne = self.model.generate_content(instruction)
        return self.utils._parse_episode_response(reposne.text, {})

    def _summarize_key_events(
        self, key_events: List[str], characters: List[Dict[str, Any]], episode_info: str
    ) -> str:
        character_names = [char.get("Name", "") for char in characters]
        episode_info_parts = episode_info.lower().split()
        filtered_events = []
        foundational_events = []
        for event in key_events:
            if any(
                marker in event.lower() for marker in ["crucial", "major", "important"]
            ):
                foundational_events.append(event)
                continue
            if any(char_name.lower() in event.lower() for char_name in character_names):
                filtered_events.append(event)
                continue
            if any(term in event.lower() for term in episode_info_parts):
                filtered_events.append(event)
                continue
        important_events = (
            foundational_events
            + filtered_events[: max(0, 10 - len(foundational_events))]
        )
        return (
            "Key Story Events: " + "; ".join(important_events)
            if important_events
            else "No key events yet."
        )

    def _get_phase_description(self, current_phase: str) -> str:
        story_phases = self.utils.story_phases 
        return (
            "\n".join(
                desc for phase, desc in story_phases.items() if phase in current_phase
            )
            + "\n"
        )

    def _get_phase_transition_guide(self, current_phase: str, next_phase: str) -> str:
        transition_guides = {
            "Exposition-Inciting Incident": """
                    - Bridge the normal world to the inciting event with subtle foreshadowing
                    - Show the protagonist's routine/worldview just before disruption
                    - Create contrast between "before" and "after" states
                    - Use sensory details that hint at the coming change
                """,
            "Inciting Incident-Rising Action": """
                    - Show the protagonist's immediate emotional reaction to the inciting event
                    - Illustrate their decision to engage with the new situation
                    - Introduce secondary characters who will aid or hinder progress
                    - Begin complicating the initial problem with new obstacles
                """,
            "Rising Action-Dilemma": """
                    - Escalate stakes to force a critical decision point
                    - Create a situation where the protagonist's old methods fail
                    - Bring conflicting values or goals into direct opposition
                    - Reveal new information that changes the protagonist's understanding
                """,
            "Dilemma-Climax": """
                    - Show the resolution of the dilemma through a meaningful choice
                    - Accelerate pacing with shorter sentences and immediate action
                    - Bring key characters into direct confrontation
                    - Create a point of return moment that commits to resolution
                """,
            "Climax-Denouement": """
                    - Show immediate aftermath and emotional impact of the climax
                    - Begin resolving secondary conflicts and character arcs
                    - Reflect on how the protagonist has changed from beginning to end
                    - Create symmetry with opening through mirrored imagery or situations
                """,
            "Denouement-Final Episode": """
                    - Conclude the journey with a definitive settling of the world and characters’ lives.  
                    - Depict the protagonist actively shaping their future, cementing their growth.  
                    - End with a poignant, grounded moment—dialogue, action, or imagery—that echoes the story’s heart and leaves no ambiguity.
                """
        }
        return transition_guides.get(f"{current_phase}-{next_phase}", "")
