from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
import re
import json


class HumanValidation:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.DEFAULT_BATCH_SIZE = 2

    def process_episode_batches_with_human_feedback(
        self,
        story_id: int,
        num_episodes: int,
        hinglish: bool = False,
        batch_size: int = 1,
    ) -> Dict[str, Any]:
        story_data = self.db_service.get_story_info(story_id)
        if "error" in story_data:
            return {"error": story_data["error"], "episodes": []}

        metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": story_data.get("current_episode", 1),
            "num_episodes": num_episodes,
            "story_id": story_id,
            "characters": story_data["characters"],
            "hinglish": hinglish,
        }
        all_episodes = []
        current_batch_start = 1
        effective_batch_size = batch_size if batch_size else self.DEFAULT_BATCH_SIZE

        while current_batch_start <= num_episodes:
            batch_end = min(
                current_batch_start + effective_batch_size - 1, num_episodes
            )
            episode_batch = self._generate_batch(
                story_id,
                current_batch_start,
                batch_end,
                metadata,
                all_episodes,
                hinglish,
            )

            print(f"Batch {current_batch_start}-{batch_end}:")
            for ep in episode_batch:
                print(
                    f"Episode {ep['episode_number']}: {ep['episode_title']}\n{ep['episode_content']}\n"
                )

            print(
                "Enter your feedback in natural language:\n"
                f"- 'Change episode 2 title to \"The New Title\"'\n"
                f"- 'Make episode 3 more suspenseful'\n"
                f"- 'Change this line \"Original text\" to a more dramatic line in episode 1'\n"
                f"- 'no change needed'"
            )
            feedback = input("Your changes: ").strip()

            if feedback.lower() == "no change needed":
                all_episodes.extend(episode_batch)
                current_batch_start = batch_end + 1
            else:
                changes = self._process_feedback(feedback, episode_batch)
                print(f"DEBUG: Parsed changes: {changes}")
                if changes:
                    current_batch_start = min(changes.keys())
                    all_episodes = [
                        ep
                        for ep in all_episodes
                        if ep["episode_number"] < current_batch_start
                    ]
                    while True:
                        proposed_batch = self._process_changes_with_appropriate_method(
                            story_id,
                            current_batch_start,
                            batch_end,
                            metadata,
                            all_episodes,
                            hinglish,
                            changes,
                            episode_batch,
                        )

                        print(f"Proposed Batch {current_batch_start}-{batch_end}:")
                        for ep in proposed_batch:
                            print(
                                f"Episode {ep['episode_number']}: {ep['episode_title']}\n{ep['episode_content']}\n"
                            )
                        validation = (
                            input(
                                f"Validate proposed batch {current_batch_start}-{batch_end}? (yes/no): "
                            )
                            .strip()
                            .lower()
                        )
                        if validation == "yes":
                            all_episodes.extend(proposed_batch)
                            current_batch_start = batch_end + 1
                            break
                        elif validation == "no":
                            feedback = input(
                                "What changes do you want instead? (e.g., 'Change episode 2 title to \"Another Title\"'): "
                            ).strip()
                            if feedback.lower() == "no change needed":
                                all_episodes.extend(episode_batch)
                                current_batch_start = batch_end + 1
                                break
                            changes = self._process_feedback(feedback, episode_batch)
                            print(f"DEBUG: New changes: {changes}")
                            if not changes:
                                print(
                                    "Couldn't parse feedback. Keeping original batch."
                                )
                                all_episodes.extend(episode_batch)
                                current_batch_start = batch_end + 1
                                break
                else:
                    print("Couldn't understand feedback. Skipping to next batch.")
                    all_episodes.extend(episode_batch)
                    current_batch_start = batch_end + 1

        while True:
            print(
                "Any final tweaks? Use natural language like:\n"
                "- 'Change episode 3 title to \"Final Title\"'\n"
                "- 'Improve the ending of episode 2'\n"
                "- 'none'"
            )
            tweak_input = input("Your final tweaks: ").strip()
            if tweak_input.lower() == "none":
                break
            changes = self._process_feedback(tweak_input, all_episodes)
            print(f"DEBUG: Final tweak changes: {changes}")
            if changes:
                target_episode = min(changes.keys())
                all_episodes = self._tweak_specific_episodes(
                    story_id, target_episode, metadata, all_episodes, hinglish, changes
                )
            else:
                print("Couldn't understand tweak. Try again or say 'none'.")

        stored_episodes = []
        for episode in all_episodes:
            episode_id = self.db_service.store_episode(
                story_id, episode, episode["episode_number"]
            )
            stored_episodes.append(
                {
                    "episode_id": episode_id,
                    "episode_number": episode["episode_number"],
                    "episode_title": episode["episode_title"],
                    "episode_content": episode["episode_content"],
                    "episode_summary": episode.get("episode_summary", ""),
                    "episode_emotional_state": episode.get(
                        "episode_emotional_state", "neutral"
                    ),
                }
            )

        return (
            {"status": "success", "episodes": stored_episodes}
            if stored_episodes
            else {"error": "No episodes generated", "episodes": []}
        )

    def _process_feedback(
        self, feedback: str, episodes: List[Dict]
    ) -> Dict[int, List[Dict]]:
        """Interpret feedback with AI and add fallback for title changes"""
        if feedback.lower() in ["no change needed", "none"]:
            return {}

        # Fallback: Manually detect title changes if AI misfires
        title_match = re.match(
            r"change\s+episode\s+(\d+)\s+title\s+to\s+\"([^\"]+)\"", feedback.lower()
        )
        if title_match:
            ep_num = int(title_match.group(1))
            new_title = title_match.group(2)
            return {
                ep_num: [{"type": "title", "value": new_title, "instruction": feedback}]
            }

        structured_feedback = self.ai_service.interpret_feedback(
            feedback=feedback, episodes=episodes
        )
        changes = {}
        for change in structured_feedback:
            ep_num = change["episode_number"]
            if ep_num not in changes:
                changes[ep_num] = []
            change_type = change["change_type"].lower()
            if change_type == "title":
                changes[ep_num].append(
                    {
                        "type": "title",
                        "value": change.get("new_value", ""),
                        "instruction": feedback,
                    }
                )
            elif change_type == "ai_title":
                changes[ep_num].append(
                    {
                        "type": "ai_title",
                        "instruction": change.get("instruction", feedback),
                    }
                )
            elif change_type in ["line", "improved_line", "style", "content"]:
                changes[ep_num].append(
                    {
                        "type": change_type,
                        "value": change.get("new_value", ""),
                        "old_text": change.get("old_text", ""),
                        "new_text": change.get("new_text", ""),
                        "style": change.get("style", ""),
                        "instruction": change.get("instruction", feedback),
                        "line": change.get("line", ""),
                    }
                )
        return changes

    def _process_changes_with_appropriate_method(
        self,
        story_id: int,
        start: int,
        end: int,
        metadata: Dict,
        prev_episodes: List,
        hinglish: bool,
        changes: Dict[int, List[Dict]],
        original_batch: List[Dict],
    ) -> List[Dict]:
        batch = []
        for i in range(start, end + 1):
            original_episode = next(
                (ep for ep in original_batch if ep["episode_number"] == i), None
            )
            if not original_episode:
                original_episode = self.ai_service.generate_episode_helper(
                    num_episodes=metadata["num_episodes"],
                    metadata=metadata,
                    episode_number=i,
                    char_text=json.dumps(metadata["characters"]),
                    story_id=story_id,
                    prev_episodes=prev_episodes + batch,
                    hinglish=hinglish,
                )
            episode = original_episode.copy()

            if i in changes:
                for change in changes[i]:
                    print(f"DEBUG: Applying change to Episode {i}: {change}")
                    if change["type"] == "title":
                        episode["episode_title"] = change["value"]
                    elif change["type"] == "ai_title":
                        episode["episode_title"] = (
                            self.ai_service.generate_better_title(
                                current_title=original_episode["episode_title"],
                                episode_content=episode["episode_content"],
                                story_context=metadata,
                                instruction=change["instruction"],
                            )
                        )
                    elif change["type"] == "line":
                        if change["old_text"] in episode["episode_content"]:
                            episode["episode_content"] = episode[
                                "episode_content"
                            ].replace(change["old_text"], change["new_text"])
                        else:
                            episode["episode_content"] = (
                                self.ai_service.replace_similar_text(
                                    episode["episode_content"],
                                    change["old_text"],
                                    change["new_text"],
                                )
                            )
                    elif change["type"] == "improved_line":
                        episode["episode_content"] = self.handle_line_improvement(
                            episode["episode_content"],
                            change["line"],
                            change.get("style", "better"),
                        )
                    elif change["type"] == "style":
                        episode["episode_content"] = (
                            self.ai_service.enhance_content_style(
                                episode["episode_content"],
                                style=change["style"],
                                story_context=metadata,
                            )
                        )
                    elif change["type"] == "content":
                        episode["episode_content"] = (
                            self.ai_service._apply_human_input1(
                                episode["episode_content"], change["instruction"]
                            )
                        )
            batch.append(episode)
        return batch

    def handle_line_improvement(self, episode_content, line_to_change, style="better"):
        if line_to_change in episode_content:
            improved_line = self.ai_service.improve_line(
                original_line=line_to_change, style=style, context=episode_content
            )
            return episode_content.replace(line_to_change, improved_line)
        else:
            return self.ai_service.replace_similar_text_with_improved(
                content=episode_content, approximate_text=line_to_change, style=style
            )

    def _generate_batch(
        self,
        story_id: int,
        start: int,
        end: int,
        metadata: Dict,
        prev_episodes: List,
        hinglish: bool,
    ) -> List[Dict]:
        batch = []
        for i in range(start, end + 1):
            episode = self.ai_service.generate_episode_helper(
                num_episodes=metadata["num_episodes"],
                metadata=metadata,
                episode_number=i,
                char_text=json.dumps(metadata["characters"]),
                story_id=story_id,
                prev_episodes=prev_episodes + batch,
                hinglish=hinglish,
            )
            batch.append(episode)
        return batch

    def _tweak_specific_episodes(
        self,
        story_id: int,
        target_episode: int,
        metadata: Dict,
        all_episodes: List,
        hinglish: bool,
        changes: Dict[int, List[Dict]],
    ) -> List[Dict]:
        batch_start = target_episode - ((target_episode - 1) % self.DEFAULT_BATCH_SIZE)
        batch_end = min(
            batch_start + self.DEFAULT_BATCH_SIZE - 1, metadata["num_episodes"]
        )
        prev_episodes = [
            ep for ep in all_episodes if ep["episode_number"] < batch_start
        ]
        original_batch = [
            ep
            for ep in all_episodes
            if batch_start <= ep["episode_number"] <= batch_end
        ]
        if not original_batch:
            original_batch = self._generate_batch(
                story_id, batch_start, batch_end, metadata, prev_episodes, hinglish
            )

        while True:
            proposed_batch = self._process_changes_with_appropriate_method(
                story_id,
                batch_start,
                batch_end,
                metadata,
                prev_episodes,
                hinglish,
                changes,
                original_batch,
            )

            print(f"Proposed Updated Episodes:")
            for ep in proposed_batch:
                print(
                    f"Episode {ep['episode_number']}: {ep['episode_title']}\n{ep['episode_content']}\n"
                )
            validation = input("Validate proposed episodes? (yes/no): ").strip().lower()

            if validation == "yes":
                result = [
                    ep for ep in all_episodes if ep["episode_number"] < batch_start
                ]
                result.extend(proposed_batch)
                result.extend(
                    [ep for ep in all_episodes if ep["episode_number"] > batch_end]
                )
                return result
            elif validation == "no":
                tweak_input = input(
                    "What changes do you want instead? (e.g., 'Change episode 2 title to \"Another Title\"') or 'none': "
                ).strip()
                if tweak_input.lower() == "none":
                    return all_episodes
                changes = self._process_feedback(tweak_input, original_batch)
                print(f"DEBUG: New tweak changes: {changes}")
                if not changes:
                    print("Couldn't parse tweak. Try again or say 'none'.")
