import json
import re
from typing import Dict, List, Any
from app.services.embedding_service import EmbeddingService


class AIGeneration:
    def __init__(self, model, embedding_service: EmbeddingService):
        self.model = model
        self.embedding_service = embedding_service

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict[str, Any],
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List[Dict[str, Any]] = [],
        hinglish: bool = False,
    ) -> Dict[str, Any]:
        settings_data = (
            "\n".join(
                f"{place}: {description}"
                for place, description in metadata.get("setting", {}).items()
            )
            or "No settings provided. Build your own."
        )
        print(f"prev_episodes: {prev_episodes}\n")
        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep.get('number', 'N/A')}\nCONTENT: {ep.get('content', 'No content')}\nTITLE: {ep.get('title', 'No title')}"
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
        # Ensure characters is a List[Dict[str, Any]]
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

        transition_guide = (
            self._get_phase_transition_guide(current_phase, next_phase)
            if next_phase
            else ""
        )
        key_events_summary = self._summarize_key_events(
            metadata.get("key_events", []), characters, episode_info
        )  # Pass typed characters
        hinglish_instruction = (
            "Use pure Hinglish for *all fields* (e.g., 'Arjun ka dar', not 'Arjun's fear')"
            if hinglish
            else ""
        )
        phase_description = self._get_phase_description(current_phase)

        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" for engaging narration.
        {hinglish_instruction} Episode {episode_number} of {num_episodes} (Target: 300-400 words).
        The story is set in diverse environments inspired by "{settings_data}", but avoid repetitive weather references (e.g., rain) unless critical to the plot. Vary the opening line with actions, dialogue, or unexpected events instead of fixed patterns.

        ---
        CURRENT_PHASE: {current_phase}
        Brief of things that should happen in this phase: {episode_info}
        PHASE REQUIREMENTS: 
        {phase_description}
        TRANSITION TO NEXT PHASE ({next_phase if next_phase else 'None'}):
        {transition_guide}

        GUIDELINES:
        - Use Character Snapshot to track arcs and relationships, but shift focus to secondary characters or subplots at least once per episode.
        - Reference Relevant Context selectively—blend past events with fresh narrative elements to avoid repetition.
        - Start story with some backstory (don't do sudden introduction of char . smooth development should be there)
        - When ever introduce a new character, show their backstory and introduce their role in the story.
        - Introduce characters with unique hooks reflecting their current state, varying their presentation (e.g., through others' eyes, internal monologue).
        - Whenever remove a character, show their departure and the impact on the story properly.
        - End with a lead-in to the next episode unless final, reflecting the transition guide if applicable, and introduce a new twist or perspective.
        - Use sensory-rich descriptions and varied dialogue, alternating tone (e.g., tense, reflective, humorous) to keep the style dynamic.

        Previous Episodes Recap: {prev_episodes_text} (use sparingly to avoid over-reliance).
        Relevant Context: {chunks_text} (integrate creatively, not as a template).
        Character Snapshot: {char_snapshot}
        Key Events So Far: {key_events_summary}

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_title": "A descriptive, Pronounceable Title",
          "episode_content": "An immersive episode with compelling storytelling and varied style."
        }}
        """
        first_response = self.model.generate_content(instruction)
        title_content_data = self._parse_episode_response(first_response.text, metadata)

        details_instruction = f"""
        Based on the episode title and content, generate details for "{metadata.get('title', 'Untitled Story')}" Episode {episode_number}.
        {hinglish_instruction}
        Title: {title_content_data['episode_title']}
        Content: {title_content_data['episode_content']}

        GUIDELINES:
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
        details_data = self._parse_and_clean_response(second_response.text, metadata)

        complete_episode = {
            "episode_number": episode_number,
            "episode_title": title_content_data["episode_title"],
            "episode_content": title_content_data["episode_content"],
            **details_data,
        }
        return self._parse_episode_response(json.dumps(complete_episode), metadata)

    def _parse_episode_response(
        self, response_text: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
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
            json_pattern2 = r'{[\s\S]*"episode_title"[\s\S]*"episode_content"[\s\S]*}'
            match = re.search(json_pattern2, response_text)
            if match:
                try:
                    cleaned_json = match.group(0).replace("'", '"')
                    return json.loads(cleaned_json)
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

    def _parse_and_clean_response(
        self, raw_text: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        if "```json" in raw_text:
            raw_text = re.sub(r"```json\s*|\s*```", "", raw_text)
        elif "```" in raw_text:
            raw_text = re.sub(r"```\s*|\s*```", "", raw_text)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            clean_text = "".join(ch for ch in raw_text if ch.isprintable())
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON parsing failed with error: {e}")
                print(f"DEBUG: Raw text:\n{raw_text}\n")
                return {
                    "episode_summary": "Summary placeholder due to parsing error.",
                    "episode_emotional_state": "neutral",
                    "characters_featured": [],
                    "Key Events": [{"event": "Default event", "tier": "contextual"}],
                    "Settings": {},
                }

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
        story_phases = {
            "Exposition": """
            - Set the scene with vivid sensory details (sight, sound, smell) and atmosphere.  
            - Introduce the protagonist via actions and thoughts, showing their normal world and backstory.  
            - Highlight strengths, flaws, and routines through interactions.  
            - Subtly hint at tensions or themes to come.
            """,
            "Inciting Incident": """
            - Disrupt the status quo with a mysterious, tense, or unexpected event.  
            - Hook with a moment demanding the protagonist's response.  
            - Plant seeds of the central conflict without full reveal.  
            - Raise stakes to push the story forward.
            """,
            "Rising Action": """
            - Escalate obstacles testing the protagonist's values and skills.  
            - Deepen character bonds or conflicts through shared challenges.  
            - Reveal backstory and complications forcing tough choices.  
            - Build tension with pacing and a mini-cliffhanger raising stakes.
            """,
            "Dilemma": """
            - Present a multi-layered obstacle (emotional, moral, physical) with no easy solution.  
            - Force a pivotal choice revealing the protagonist's core beliefs.  
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
            """,
        }
        return (
            "".join(
                phase for phase, desc in story_phases.items() if phase in current_phase
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
        }
        return transition_guides.get(f"{current_phase}-{next_phase}", "")
