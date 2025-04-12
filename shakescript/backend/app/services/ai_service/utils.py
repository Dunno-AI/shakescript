from typing import Dict, Any
import json, re

class AIUtils:
    def __init__(self) -> None:
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

    def apply_human_input(self, content: str, human_input: str) -> str:
        return f"{content}\n{{ Human Change: {human_input} }}".strip()
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


