import json
from typing import Dict, List, Any
from app.services.ai_service.utilsAI import AIUtils
from app.services.embedding_service import EmbeddingService
from app.services.ai_service.prompts import AIPrompts


class AIGeneration:
    def __init__(self, model, embedding_service: EmbeddingService):
        self.model = model
        self.embedding_service = embedding_service
        self.utils = AIUtils()
        self.prompts = AIPrompts()

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

        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep.get('episode_number', 'N/A')}\nCONTENT: {ep.get(
                    'content', 'No content')}\nTITLE: {ep.get('title', 'No title')}"
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
                f"Name: {char.get('Name')}, Role: {
                    char.get('Role', 'Unknown')}, "
                f"Description: {
                    char.get('Description', 'No description available')}, "
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
            self.utils._get_phase_transition_guide(current_phase, next_phase)
            if next_phase
            else ""
        )}"""
        phase_description = f"""Things you can follow in this phase:
        {self._get_phase_description(current_phase)}"""

        PHASE_INFORMATION = (
            transition_guide
            if end == episode_number and next_phase != current_phase
            else phase_description
        )
        key_events_summary = self._summarize_key_events(
            metadata.get("key_events", []), characters, episode_info
        )

        general_pts = self.prompts.EPISODE_GENERATION_GENERAL_POINTS()
        instruction = self.prompts.EPISODE_GENERATION_PROMPT(
            metadata,
            episode_number,
            num_episodes,
            current_phase,
            PHASE_INFORMATION,
            general_pts,
            prev_episodes_text,
            chunks_text,
            char_snapshot,
            key_events_summary,
            settings_data,
            episode_info,
        )

        first_response = self.model.generate_content(instruction)
        title_content_data = self.utils._parse_episode_response(
            first_response.text, metadata
        )
        if hinglish:
            title_content_data = self.hinglish_conversion(
                title_content_data["episode_content"],
                title_content_data["episode_title"],
            )

        details_instruction = self.prompts.EPISODE_DETAIL_EXTRACTION_PROMPT(
            episode_number, metadata, title_content_data, chunks_text, char_snapshot
        )
        second_response = self.model.generate_content(details_instruction)
        details_data = self.utils._parse_and_clean_response(
            second_response.text, metadata
        )

        complete_episode = {
            "episode_number": episode_number,
            "episode_title": title_content_data["episode_title"],
            "episode_content": title_content_data["episode_content"],
            **details_data,
        }
        return self.utils._parse_episode_response(
            json.dumps(complete_episode), metadata
        )

    def hinglish_conversion(self, ep_content, ep_title) -> Dict[str, Any]:
        instruction = self.prompts.HINGLISH_PROMPT(ep_title, ep_content)
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
