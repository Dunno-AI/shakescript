from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, List
import json


class CharactersDB:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    def update_character_state(self, story_id: int, character_data: List[Dict]) -> None:
        # Separate existing characters and new characters
        for char in character_data:
            # Query for existing character
            current_char = (
                self.supabase.table("characters")
                .select("*")
                .eq("story_id", story_id)
                .eq("name", char["Name"])
                .execute()
                .data
            )

            if current_char:
                # Existing character: Update by ID
                current = current_char[0]
                new_emotional = char.get(
                    "Emotional_State", current.get("emotional_state", "neutral")
                )
                milestones = json.loads(current.get("milestones", "[]"))
                if new_emotional != current.get("emotional_state"):
                    milestones.append(
                        {
                            "event": f"Shift to {new_emotional}",
                            "episode": current.get("last_episode", 0) + 1,
                        }
                    )

                # Update existing character by ID
                self.supabase.table("characters").update(
                    {
                        "role": char.get("Role", current.get("role", "Unknown")),
                        "description": char.get(
                            "Description", current.get("description", "No description")
                        ),
                        "relationship": json.dumps(
                            {
                                **json.loads(current.get("relationship", "{}")),
                                **char.get("Relationship", {}),
                            }
                        ),
                        "is_active": char.get(
                            "role_active", current.get("is_active", True)
                        ),
                        "emotional_state": new_emotional,
                        "milestones": json.dumps(milestones[-5:]),
                        "last_episode": current.get("last_episode", 0) + 1,
                    }
                ).eq("id", current["id"]).execute()
            else:
                # New character: Insert without ID
                new_emotional = char.get("Emotional_State", "neutral")
                self.supabase.table("characters").insert(
                    {
                        "story_id": story_id,
                        "name": char["Name"],
                        "role": char.get("Role", "Unknown"),
                        "description": char.get("Description", "No description"),
                        "relationship": json.dumps(char.get("Relationship", {})),
                        "is_active": char.get("role_active", True),
                        "emotional_state": new_emotional,
                        "milestones": json.dumps([]),
                        "last_episode": 1,
                    }
                ).execute()
