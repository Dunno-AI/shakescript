from typing import Dict, List, Any
from app.services.ai_service import AIService
from app.services.db_service import DBService
from app.services.embedding_service import EmbeddingService
from app.models.schemas import StoryListItem
import json
import re


class StoryService:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()
        self.DEFAULT_BATCH_SIZE = 2 
        self.story_memory = {}

    async def create_story(
        self, prompt: str, num_episodes: int, hinglish: bool = False
    ) -> Dict[str, Any]:
        full_prompt = f"{prompt} number of episodes = {num_episodes}"
        result = self.extract_and_store_metadata(full_prompt, num_episodes, hinglish)
        return (
            result
            if "error" in result
            else {"story_id": result["story_id"], "title": result["title"]}
        )

    def extract_and_store_metadata(
        self, user_prompt: str, num_episodes: int, hinglish: bool
    ) -> Dict[str, Any]:
        metadata = self.ai_service.extract_metadata(user_prompt, num_episodes, hinglish)
        if "error" in metadata:
            return metadata
        story_id = self.db_service.store_story_metadata(metadata, num_episodes)
        return {"story_id": story_id, "title": metadata.get("Title", "Untitled Story")}

    def get_story_info(self, story_id: int) -> Dict[str, Any]:
        return self.db_service.get_story_info(story_id)

    def generate_episode(
        self,
        story_id: int,
        episode_number: int,
        num_episodes: int,
        hinglish: bool = False,
        prev_episodes=[],
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        story_metadata = {
            "title": story_data["title"],
            "setting": story_data["setting"],
            "key_events": story_data["key_events"],
            "special_instructions": story_data["special_instructions"],
            "story_outline": story_data["story_outline"],
            "current_episode": episode_number,
            "timeline": story_data["timeline"],
        }
        return self.ai_service.generate_episode_helper(
            num_episodes,
            story_metadata,
            episode_number,
            json.dumps(story_data["characters"]),
            story_id,
            prev_episodes,
            hinglish,
        )

    def get_all_stories(self) -> List[StoryListItem]:
        return [
            StoryListItem(story_id=story["id"], title=story["title"])
            for story in self.db_service.get_all_stories()
        ]

    def generate_and_store_episode(
        self,
        story_id: int,
        episode_number: int,
        num_episodes: int,
        hinglish: bool = False,
        prev_episodes=[],
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data

        episode_data = self.generate_episode(
            story_id, episode_number, num_episodes, hinglish, prev_episodes
        )
        if "error" in episode_data:
            return episode_data

        episode_id = self.db_service.store_episode(
            story_id, episode_data, episode_number
        )
        character_names = [
            char["Name"] for char in episode_data.get("characters_featured", [])
        ]
        self.embedding_service._process_and_store_chunks(
            story_id,
            episode_id,
            episode_number,
            episode_data["episode_content"],
            character_names,
        )

        return {
            "episode_id": episode_id,
            "episode_number": episode_number,
            "episode_title": episode_data["episode_title"],
            "episode_content": episode_data["episode_content"],
            "episode_summary": episode_data.get("episode_summary", ""),
            "episode_emotional_state": episode_data.get(
                "episode_emotional_state", "neutral"
            ),
        }

    def generate_multiple_episodes(
        self, story_id: int, num_episodes: int, hinglish: bool = False
    ) -> List[Dict[str, Any]]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return [story_data]

        episodes = []
        current_episode = story_data["current_episode"]
        for i in range(num_episodes):
            episode_number = current_episode + i
            prev_episodes = [
                {
                    "episode_number": ep["episode_number"],
                    "content": ep["episode_content"],
                    "title": ep["episode_title"],
                }
                for ep in episodes[-2:]
            ]
            episode_result = self.generate_and_store_episode(
                story_id, episode_number, num_episodes, hinglish, prev_episodes
            )
            if "error" in episode_result:
                return episodes + [episode_result]
            episodes.append(episode_result)
        return episodes

    def process_episode_batches_with_human_feedback(
        self, story_id: int, num_episodes: int, hinglish: bool = False
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
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
        story_memory = {
            "characters": {c["Name"]: c for c in story_data["characters"]},
            "key_events": story_data["key_events"],
            "settings": story_data["setting"],
            "arcs": [],
        }
        all_episodes = []
        current_batch_start = 1
        batch_size = (
            num_episodes
            if num_episodes == metadata["num_episodes"]
            else self.DEFAULT_BATCH_SIZE
        )

        while current_batch_start <= num_episodes:
            batch_end = min(current_batch_start + batch_size - 1, num_episodes)
            episode_batch = self._generate_batch(
                story_id,
                current_batch_start,
                batch_end,
                metadata,
                all_episodes,
                hinglish,
            )

            # Display full episode content
            print(f"Batch {current_batch_start}-{batch_end}:")
            for ep in episode_batch:
                print(
                    f"Episode {ep['episode_number']}: {ep['episode_title']}\nContent: {ep['episode_content']}\n"
                )

            # Get human feedback (support multi-episode tweaks)
            feedback = input(
                f"Enter changes (e.g., 'Episode {current_batch_start}: change only title to New Title; Episode {batch_end}: Fix ending') or 'no change needed': "
            ).strip()
            if feedback.lower() == "no change needed":
                all_episodes.extend(episode_batch)
                current_batch_start = batch_end + 1
            else:
                # Parse multi-episode feedback with specific instructions
                changes = {}
                for change in feedback.split(";"):
                    change = change.strip()
                    match = re.match(r"Episode (\d+):(.*)", change)
                    if match:
                        target_episode = int(match.group(1))
                        change_desc = match.group(2).strip()
                        # Check for "change only title" instruction
                        if "change only title" in change_desc.lower():
                            title_match = re.search(r"to\s+(.+)", change_desc)
                            if title_match:
                                new_title = title_match.group(1).strip()
                                changes[target_episode] = {
                                    "type": "title",
                                    "value": new_title,
                                }
                        else:
                            changes[target_episode] = {
                                "type": "content",
                                "value": change_desc,
                            }
                if changes:
                    # Regenerate the same batch with tweaks
                    current_batch_start = min(changes.keys())
                    all_episodes = [
                        ep
                        for ep in all_episodes
                        if ep["episode_number"] < current_batch_start
                    ]
                    episode_batch = self._regenerate_batch_with_changes(
                        story_id,
                        current_batch_start,
                        batch_end,
                        metadata,
                        all_episodes,
                        hinglish,
                        changes,
                    )
                    # Revalidate the updated batch
                    print(f"Updated Batch {current_batch_start}-{batch_end}:")
                    for ep in episode_batch:
                        print(
                            f"Episode {ep['episode_number']}: {ep['episode_title']}\nContent: {ep['episode_content']}\n"
                        )
                    validation = (
                        input(
                            f"Validate updated batch {current_batch_start}-{batch_end}? (yes/no): "
                        )
                        .strip()
                        .lower()
                    )
                    if validation == "yes":
                        all_episodes.extend(episode_batch)
                        current_batch_start = batch_end + 1
                    else:
                        # Retry the same batch
                        continue
                else:
                    print("Invalid feedback format. Skipping to next batch.")
                    all_episodes.extend(episode_batch)
                    current_batch_start = batch_end + 1

        # Final tweaking option with validation
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

        # Store all episodes
        stored_episodes = []
        for episode in all_episodes:
            episode_id = self.db_service.store_episode(
                story_id, episode, episode["episode_number"]
            )
            self._update_story_memory(story_id, episode)
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

    def process_episode_batches_with_ai_validation(
        self, story_id: int, num_episodes: int, hinglish: bool = False
    ) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
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
        story_memory = {
            "characters": {c["Name"]: c for c in story_data["characters"]},
            "key_events": story_data["key_events"],
            "settings": story_data["setting"],
            "arcs": [],
        }
        all_episodes = []
        current_batch_start = 1
        batch_size = (
            num_episodes
            if num_episodes == metadata["num_episodes"]
            else self.DEFAULT_BATCH_SIZE
        )

        while current_batch_start <= num_episodes:
            batch_end = min(current_batch_start + batch_size - 1, num_episodes)
            episode_batch = self._generate_batch(
                story_id,
                current_batch_start,
                batch_end,
                metadata,
                all_episodes,
                hinglish,
            )

            # Validate with Gemini in a loop until valid
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

            # Display full episode content for transparency
            print(f"Validated Batch {current_batch_start}-{batch_end}:")
            for ep in episode_batch:
                print(
                    f"Episode {ep['episode_number']}: {ep['episode_title']}\nContent: {ep['episode_content']}\n"
                )

            all_episodes.extend(episode_batch)
            current_batch_start = batch_end + 1

        # Final tweaking option with validation
        tweak_input = input(
            "Any final tweaks? (e.g., 'Episode 3: change this part') or 'none': "
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

        # Store all episodes
        stored_episodes = []
        for episode in all_episodes:
            episode_id = self.db_service.store_episode(
                story_id, episode, episode["episode_number"]
            )
            self._update_story_memory(story_id, episode)
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

        # Regenerate the batch with tweaks
        episode_batch = self._regenerate_batch_with_changes(
            story_id, batch_start, batch_end, metadata, prev_episodes, hinglish, changes
        )

        # Display and validate the updated batch
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
            all_episodes = [
                ep for ep in all_episodes if ep["episode_number"] < batch_start
            ] + episode_batch
        else:
            all_episodes = self._tweak_and_regenerate_with_validation(
                story_id, target_episode, metadata, all_episodes, hinglish, changes
            )
        return all_episodes

    def _validate_batch_with_gemini(
        self, episode_batch: List[Dict], metadata: Dict
    ) -> bool:
        content = "\n".join(ep["episode_content"] for ep in episode_batch)
        instruction = f"Validate this batch of episodes for coherence, plot integrity, character consistency, and overall storytelling quality:\n{content}\nReturn 'valid' if correct, 'invalid' with reasons otherwise."
        response = self.ai_service.model.generate_content(instruction)
        print(f"Validation Response: {response.text}")
        return "valid" in response.text.lower()

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

    def _update_story_memory(self, story_id: int, episode_data: Dict):
        if story_id not in self.__dict__.get("story_memory", {}):
            self.story_memory = self.story_memory or {}
            self.story_memory[story_id] = {
                "characters": {},
                "key_events": [],
                "settings": {},
                "arcs": [],
            }
        memory = self.story_memory[story_id]
        memory["characters"].update(
            {char["Name"]: char for char in episode_data.get("characters_featured", [])}
        )
        memory["key_events"].extend(episode_data.get("Key Events", []))
        memory["settings"].update(episode_data.get("Settings", {}))
        memory["arcs"].append(
            {
                "episode_number": episode_data["episode_number"],
                "phase": episode_data.get("current_phase", "Unknown"),
            }
        )

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return {"error": story_data["error"]}
        episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
        instruction = f"Create a 150-200 word audio teaser summary for '{story_data['title']}' based on: {episode_summaries}. Use vivid, short sentences. End with a hook."
        summary = self.ai_service.model.generate_content(instruction).text.strip()
        self.db_service.supabase.table("stories").update({"summary": summary}).eq(
            "id", story_id
        ).execute()
        return {"status": "success", "summary": summary}
