# app/services/db_service/charactersDB.py

from supabase import Client
from typing import Dict, List
import json


class CharactersDB:
    def __init__(self, client: Client):
        """
        KEY CHANGE: Accept the authenticated client.
        """
        self.client = client

    def update_character_state(
        self, story_id: int, character_data: List[Dict], auth_id: str
    ) -> None:
        if not character_data:
            return

        for char in character_data:
            current_char_res = (
                self.client.table("characters")
                .select("*")
                .eq("story_id", story_id)
                .eq("auth_id", auth_id)
                .eq("name", char["Name"])
                .execute()
            )
            current_char_list = current_char_res.data

            if current_char_list:
                current = current_char_list[0]
                new_emotional = char.get(
                    "Emotional_State", current.get("emotional_state", "neutral")
                )
                milestones = json.loads(current.get("milestones", "[]") or "[]")
                if new_emotional != current.get("emotional_state"):
                    milestones.append(
                        {
                            "event": f"Shift to {new_emotional}",
                            "episode": current.get("last_episode", 0) + 1,
                        }
                    )

                self.client.table("characters").update(
                    {
                        "role": char.get("Role", current.get("role", "Unknown")),
                        "description": char.get(
                            "Description", current.get("description", "No description")
                        ),
                        "relationship": json.dumps(
                            {
                                **json.loads(current.get("relationship", "{}") or "{}"),
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
                ).eq("id", current["id"]).eq("auth_id", auth_id).execute()
            else:
                new_emotional = char.get("Emotional_State", "neutral")
                self.client.table("characters").insert(
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
                        "auth_id": auth_id,
                    }
                ).execute()
