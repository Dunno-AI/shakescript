from typing import Dict

class AIUtils:
    def apply_human_input(self, content: str, human_input: str) -> str:
        return f"{content}\n{{ Human Change: {human_input} }}".strip()
