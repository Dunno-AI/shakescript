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
        self.BATCH_SIZE = 2  # Adjustable batch size

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

    def process_episode_batches_with_human_feedback(self, story_id: int, num_episodes: int, hinglish: bool = False) -> List[Dict[str, Any]]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return [story_data]
        
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
            "hinglish": hinglish
        }
        story_memory = {"characters": {c["Name"]: c for c in story_data["characters"]}, "key_events": story_data["key_events"], "settings": story_data["setting"], "arcs": []}
        all_episodes = []
        current_batch_start = 1

        while current_batch_start <= num_episodes:
            batch_end = min(current_batch_start + self.BATCH_SIZE - 1, num_episodes)
            episode_batch = self._generate_batch(story_id, current_batch_start, batch_end, metadata, all_episodes, hinglish)
            
            # Display batch (simulated here, replace with UI logic)
            print(f"Batch {current_batch_start}-{batch_end}: {len(episode_batch)} episodes")
            for ep in episode_batch:
                print(f"Episode {ep['episode_number']}: {ep['episode_title'][:50]}...")
            
            # Get human feedback (simulated input, replace with UI)
            feedback = input("Enter changes (e.g., 'Episode 2: Add suspense') or 'no change needed': ").strip()
            if feedback.lower() == "no change needed":
                all_episodes.extend(episode_batch)
                current_batch_start = batch_end + 1
            else:
                # Parse feedback for specific episode
                match = re.match(r"Episode (\d+):(.+)", feedback)
                if match:
                    target_episode = int(match.group(1))
                    change_desc = match.group(2).strip()
                    # Regenerate from target episode onwards
                    current_batch_start = target_episode
                    all_episodes = [ep for ep in all_episodes if ep["episode_number"] < target_episode]
                    episode_batch = self._regenerate_from_episode(story_id, target_episode, num_episodes, metadata, all_episodes, hinglish, change_desc)
                    all_episodes.extend(episode_batch)
                    current_batch_start = max(ep["episode_number"] for ep in episode_batch) + 1
                else:
                    print("Invalid feedback format. Skipping to next batch.")
                    all_episodes.extend(episode_batch)
                    current_batch_start = batch_end + 1
        
        # Final tweaking option
        tweak_input = input("Any final tweaks? (e.g., 'Episode 3: Fix ending') or 'none': ").strip()
        if tweak_input.lower() != "none":
            match = re.match(r"Episode (\d+):(.+)", tweak_input)
            if match:
                target_episode = int(match.group(1))
                tweak_desc = match.group(2).strip()
                all_episodes = self._tweak_and_regenerate(story_id, target_episode, tweak_desc, metadata, all_episodes, hinglish)
        
        # Store all episodes
        for episode in all_episodes:
            episode_id = self.db_service.store_episode(story_id, episode, episode["episode_number"])
            self._update_story_memory(story_id, episode)
        
        return [{
            "episode_id": episode_id,
            "episode_number": ep["episode_number"],
            "episode_title": ep["episode_title"],
            "episode_content": ep["episode_content"],
            "episode_summary": ep.get("episode_summary", ""),
            "episode_emotional_state": ep.get("episode_emotional_state", "neutral"),
        } for ep in all_episodes]

    def process_episode_batches_with_ai_validation(self, story_id: int, num_episodes: int, hinglish: bool = False) -> List[Dict[str, Any]]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return [story_data]
        
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
            "hinglish": hinglish
        }
        story_memory = {"characters": {c["Name"]: c for c in story_data["characters"]}, "key_events": story_data["key_events"], "settings": story_data["setting"], "arcs": []}
        all_episodes = []
        current_batch_start = 1

        while current_batch_start <= num_episodes:
            batch_end = min(current_batch_start + self.BATCH_SIZE - 1, num_episodes)
            episode_batch = self._generate_batch(story_id, current_batch_start, batch_end, metadata, all_episodes, hinglish)
            
            # Validate batch with Gemini
            if not self._validate_batch_with_gemini(episode_batch, metadata):
                # Regenerate the same batch
                episode_batch = self._regenerate_batch(story_id, current_batch_start, batch_end, metadata, all_episodes, hinglish)
            
            all_episodes.extend(episode_batch)
            current_batch_start = batch_end + 1
        
        # Final tweaking option
        tweak_input = input("Any final tweaks? (e.g., 'Episode 3: Fix ending') or 'none': ").strip()
        if tweak_input.lower() != "none":
            match = re.match(r"Episode (\d+):(.+)", tweak_input)
            if match:
                target_episode = int(match.group(1))
                tweak_desc = match.group(2).strip()
                all_episodes = self._tweak_and_regenerate(story_id, target_episode, tweak_desc, metadata, all_episodes, hinglish)
        
        # Store all episodes
        for episode in all_episodes:
            episode_id = self.db_service.store_episode(story_id, episode, episode["episode_number"])
            self._update_story_memory(story_id, episode)
        
        return [{
            "episode_id": episode_id,
            "episode_number": ep["episode_number"],
            "episode_title": ep["episode_title"],
            "episode_content": ep["episode_content"],
            "episode_summary": ep.get("episode_summary", ""),
            "episode_emotional_state": ep.get("episode_emotional_state", "neutral"),
        } for ep in all_episodes]

    def _generate_batch(self, story_id: int, start: int, end: int, metadata: Dict, prev_episodes: List, hinglish: bool) -> List[Dict]:
        batch = []
        for i in range(start, end + 1):
            episode = self.ai_service.generate_episode_helper(
                num_episodes=metadata["num_episodes"],
                metadata=metadata,
                episode_number=i,
                char_text=json.dumps(metadata["characters"]),
                story_id=story_id,
                prev_episodes=prev_episodes,
                hinglish=hinglish
            )
            batch.append(episode)
        return batch

    def _regenerate_from_episode(self, story_id: int, start_episode: int, num_episodes: int, metadata: Dict, prev_episodes: List, hinglish: bool, change_desc: str) -> List[Dict]:
        # Regenerate from start_episode to end
        remaining_episodes = num_episodes - start_episode + 1
        batch_size = min(self.BATCH_SIZE, remaining_episodes)
        batch = []
        for i in range(start_episode, min(start_episode + batch_size - 1, num_episodes) + 1):
            episode = self.ai_service.generate_episode_helper(
                num_episodes=metadata["num_episodes"],
                metadata=metadata,
                episode_number=i,
                char_text=json.dumps(metadata["characters"]),
                story_id=story_id,
                prev_episodes=prev_episodes,
                hinglish=hinglish
            )
            if i == start_episode:
                episode["episode_content"] = self.ai_service._apply_human_input(episode["episode_content"], change_desc)
            batch.append(episode)
        return batch

    def _tweak_and_regenerate(self, story_id: int, target_episode: int, tweak_desc: str, metadata: Dict, all_episodes: List, hinglish: bool) -> List[Dict]:
        # Find and tweak the target episode
        for ep in all_episodes:
            if ep["episode_number"] == target_episode:
                ep["episode_content"] = self.ai_service._apply_human_input(ep["episode_content"], tweak_desc)
                break
        # Regenerate affected episodes (e.g., from target onwards)
        affected_episodes = [ep for ep in all_episodes if ep["episode_number"] >= target_episode]
        new_episodes = self._regenerate_from_episode(story_id, target_episode, metadata["num_episodes"], metadata, [ep for ep in all_episodes if ep["episode_number"] < target_episode], hinglish, tweak_desc)
        all_episodes = [ep for ep in all_episodes if ep["episode_number"] < target_episode] + new_episodes
        return all_episodes

    def _validate_batch_with_gemini(self, episode_batch: List[Dict], metadata: Dict) -> bool:
        # Use Gemini to validate the batch
        content = "\n".join(ep["episode_content"] for ep in episode_batch)
        instruction = f"Validate this batch of episodes for coherence and consistency:\n{content}\nReturn 'valid' if correct, 'invalid' otherwise."
        response = self.ai_service.model.generate_content(instruction)
        return "valid" in response.text.lower()

    def _regenerate_batch(self, story_id: int, start: int, end: int, metadata: Dict, prev_episodes: List, hinglish: bool) -> List[Dict]:
        return self._generate_batch(story_id, start, end, metadata, prev_episodes, hinglish)

    def _update_story_memory(self, story_id: int, episode_data: Dict):
        if story_id not in self.__dict__.get('story_memory', {}):
            self.story_memory = self.story_memory or {}
            self.story_memory[story_id] = {
                "characters": {},
                "key_events": [],
                "settings": {},
                "arcs": []
            }
        memory = self.story_memory[story_id]
        memory["characters"].update({char["Name"]: char for char in episode_data.get("characters_featured", [])})
        memory["key_events"].extend(episode_data.get("Key Events", []))
        memory["settings"].update(episode_data.get("Settings", {}))
        memory["arcs"].append({
            "episode_number": episode_data["episode_number"],
            "phase": episode_data.get("current_phase", "Unknown")
        })

    def update_story_summary(self, story_id: int) -> Dict[str, Any]:
        story_data = self.get_story_info(story_id)
        if "error" in story_data:
            return story_data
        episode_summaries = "\n".join(ep["summary"] for ep in story_data["episodes"])
        instruction = f"Create a 150-200 word audio teaser summary for '{story_data['title']}' based on: {episode_summaries}. Use vivid, short sentences. End with a hook."
        summary = self.ai_service.model.generate_content(instruction).text.strip()
        self.db_service.supabase.table("stories").update({"summary": summary}).eq(
            "id", story_id
        ).execute()
        return {"story_id": story_id, "summary": summary}
