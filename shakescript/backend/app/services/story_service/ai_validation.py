from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
import re, json


class AIValidation:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.DEFAULT_BATCH_SIZE = 2

    def process_episode_batches_with_ai_validation(
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
        if num_episodes == metadata["num_episodes"]:
            effective_batch_size = num_episodes

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

            is_valid = False
            while not is_valid:
                is_valid = self._validate_batch_with_gemini(episode_batch, metadata)
                if not is_valid:
                    print(
                        f"Batch {current_batch_start}-{batch_end} is invalid. Regenerating..."
                    )
                    episode_batch = self._regenerate_batch(
                        story_id,
                        current_batch_start,
                        batch_end,
                        metadata,
                        all_episodes,
                        hinglish,
                    )
                else:
                    print(
                        f"Batch {current_batch_start}-{batch_end} validated successfully."
                    )

            print(f"Validated Batch {current_batch_start}-{batch_end}:")
            for ep in episode_batch:
                print(
                    f"Episode {ep['episode_number']}: {ep['episode_title']}\nContent: {ep['episode_content']}\n"
                )

            all_episodes.extend(episode_batch)
            current_batch_start = batch_end + 1

        tweak_input = input(
            "Any final tweaks? (e.g., 'Episode 3: change only title to Final Title') or 'none': "
        ).strip()
        if tweak_input.lower() != "none":
            match = re.match(r"Episode (\d+):(.*)", tweak_input)
            if match:
                target_episode = int(match.group(1))
                tweak_desc = match.group(2).strip()
                changes = {}
                if "change only title" in tweak_desc.lower():
                    title_match = re.search(r"to\s+(.+)", tweak_desc)
                    if title_match:
                        new_title = title_match.group(1).strip()
                        changes[target_episode] = {"type": "title", "value": new_title}
                else:
                    changes[target_episode] = {"type": "content", "value": tweak_desc}
                all_episodes = self._tweak_and_regenerate_with_validation(
                    story_id, target_episode, metadata, all_episodes, hinglish, changes
                )

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
                prev_episodes=prev_episodes,
                hinglish=hinglish,
            )
            batch.append(episode)
        return batch

    def _regenerate_batch(
        self,
        story_id: int,
        start: int,
        end: int,
        metadata: Dict,
        prev_episodes: List,
        hinglish: bool,
    ) -> List[Dict]:
        return self._generate_batch(
            story_id, start, end, metadata, prev_episodes, hinglish
        )

    def _validate_batch_with_gemini(
        self, episode_batch: List[Dict], metadata: Dict
    ) -> bool:
        content = "\n".join(ep["episode_content"] for ep in episode_batch)
        instruction = f"Validate this batch of episodes for coherence, plot integrity, character consistency, and overall storytelling quality:\n{content}\nReturn 'valid' if correct, 'invalid' with reasons otherwise."
        response = self.ai_service.model.generate_content(instruction)
        print(f"Validation Response: {response.text}")
        return "valid" in response.text.lower()

    def _tweak_and_regenerate_with_validation(
        self,
        story_id: int,
        target_episode: int,
        metadata: Dict,
        all_episodes: List,
        hinglish: bool,
        changes: Dict[int, Dict[str, str]],
    ) -> List[Dict]:
        batch_start = target_episode - ((target_episode - 1) % self.DEFAULT_BATCH_SIZE)
        batch_end = min(
            batch_start + self.DEFAULT_BATCH_SIZE - 1, metadata["num_episodes"]
        )
        prev_episodes = [
            ep for ep in all_episodes if ep["episode_number"] < batch_start
        ]

        episode_batch = self._regenerate_batch_with_changes(
            story_id, batch_start, batch_end, metadata, prev_episodes, hinglish, changes
        )

        print(f"Updated Batch {batch_start}-{batch_end}:")
        for ep in episode_batch:
            print(
                f"Episode {ep['episode_number']}: {ep['episode_title']}\nContent: {ep['episode_content']}\n"
            )
        validation = (
            input(f"Validate updated batch {batch_start}-{batch_end}? (yes/no): ")
            .strip()
            .lower()
        )
        if validation == "yes":
            return [
                ep for ep in all_episodes if ep["episode_number"] < batch_start
            ] + episode_batch
        else:
            return self._tweak_and_regenerate_with_validation(
                story_id, target_episode, metadata, all_episodes, hinglish, changes
            )

    def _regenerate_batch_with_changes(
        self,
        story_id: int,
        start: int,
        end: int,
        metadata: Dict,
        prev_episodes: List,
        hinglish: bool,
        changes: Dict[int, Dict[str, str]],
    ) -> List[Dict]:
        batch = []
        for i in range(start, end + 1):
            episode = self.ai_service.generate_episode_helper(
                num_episodes=metadata["num_episodes"],
                metadata=metadata,
                episode_number=i,
                char_text=json.dumps(metadata["characters"]),
                story_id=story_id,
                prev_episodes=prev_episodes,
                hinglish=hinglish,
            )
            if i in changes:
                change = changes[i]
                if change["type"] == "title":
                    episode["episode_title"] = change["value"]
                elif change["type"] == "content":
                    episode["episode_content"] = self.ai_service._apply_human_input(
                        episode["episode_content"], change["value"]
                    )
            batch.append(episode)
        return batch
