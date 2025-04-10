from typing import Dict, List, Any , Optional
from app.services.ai_service import AIService
from app.services.db_service import DBService
from app.services.embedding_service import EmbeddingService
import json


class RegenerationService:
    def __init__(self):
        self.ai_service = AIService()
        self.db_service = DBService()
        self.embedding_service = EmbeddingService()
        self.DEFAULT_BATCH_SIZE = 2

    def _regenerate_batch(
        self,
        story_id: int,
        start_episode: int,
        end_episode: int,
        metadata: Dict[str, Any],
        prev_episodes: List[Dict[str, Any]],
        hinglish: bool = False,
        feedback: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Regenerate a batch of episodes using optional AI feedback.
        Only generates the episodes without storing or chunking them.
        """
        feedback_map = {}
        if feedback:
            batch_feedback = [item for item in feedback 
                            if start_episode <= item["episode_number"] <= end_episode]
            
            for item in batch_feedback:
                ep_num = item["episode_number"]
                feedback_map.setdefault(ep_num, []).append(item["feedback"])

        batch = []
        for i in range(start_episode, end_episode + 1):
            instructions = feedback_map.get(i, [])
            combined_instruction = "\n".join(instructions) if instructions else None

            try:
                episode = self.ai_service.generate_episode_helper(
                    num_episodes=metadata["num_episodes"],
                    metadata=metadata,
                    episode_number=i,
                    char_text=json.dumps(metadata["characters"]),
                    story_id=story_id,
                    prev_episodes=prev_episodes + batch,
                    hinglish=hinglish,
                    feedback=combined_instruction
                )
            except TypeError:
                episode = self.ai_service.generate_episode_helper(
                    num_episodes=metadata["num_episodes"],
                    metadata=metadata,
                    episode_number=i,
                    char_text=json.dumps(metadata["characters"]),
                    story_id=story_id,
                    prev_episodes=prev_episodes + batch,
                    hinglish=hinglish
                )

            batch.append(episode)

        return batch

    def _store_batch_after_validation(
        self,
        story_id: int, 
        validated_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Store and process validated batch of episodes.
        """
        stored_episodes = []
        for episode in validated_batch:
            episode_id = self.db_service.store_episode(
                story_id, episode, episode["episode_number"]
            )
            
            stored_episode = {
                "episode_id": episode_id,
                "episode_number": episode["episode_number"],
                "episode_title": episode["episode_title"],
                "episode_content": episode["episode_content"],
                "episode_summary": episode.get("episode_summary", ""),
                "episode_emotional_state": episode.get("episode_emotional_state", "neutral"),
            }
            
            character_names = [
                char["Name"] for char in episode.get("characters_featured", [])
            ]
            if episode.get("episode_content"):
                self.embedding_service._process_and_store_chunks(
                    story_id,
                    episode_id,
                    episode["episode_number"],
                    episode["episode_content"],
                    character_names,
                )
                print(f"Chunking completed for episode {episode['episode_number']}")
            else:
                print(f"Warning: No episode_content for episode {episode['episode_number']}")
                
            stored_episodes.append(stored_episode)
            
        return stored_episodes

    def _validate_batch(self, episode_batch: List[Dict], metadata: Dict) -> Dict[str, Any]:
        """
        Validates a batch of episodes and returns structured feedback.
        Returns:
            - {'valid': True} if batch is valid
            - {'valid': False, 'feedback': [...]} with structured feedback if invalid
        """
        content = "\n".join(ep["episode_content"] for ep in episode_batch)
        instruction = (
            f"Validate this batch for coherence, plot integrity, and character consistency:\n{content}\n\n"
            f"If the batch is valid, simply respond with 'valid'.\n"
            f"If the batch is invalid, respond with 'invalid' followed by structured feedback "
            f"give feedback in the following format if not valid:\n"
            f"""
            {{
                "episode_number": <episode number>,
                "feedback": "<specific feedback instruction>"
            }}
            """
            f"Make your feedback specific and actionable. Do not give response in markdown format."
        )
        
        response = self.ai_service.model.generate_content(instruction)
        response_text = response.text
        print(f"AI Validation: {response_text}")
        
        if "valid" in response_text.lower() and "invalid" not in response_text.lower():
            return {"valid": True}
        
        feedback = []
        import re
        
        # Try to extract JSON objects from the response
        json_pattern = r'\{\s*"episode_number"\s*:\s*(\d+)\s*,\s*"feedback"\s*:\s*"(.+?)"\s*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            episode_number = int(match[0])
            feedback_text = match[1].strip()
            feedback.append({
                "episode_number": episode_number,
                "feedback": feedback_text
            })
        
        
        return {
            "valid": False,
            "feedback": feedback
        }
