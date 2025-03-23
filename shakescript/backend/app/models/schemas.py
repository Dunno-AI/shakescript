from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Prompt(BaseModel):
    prompt: str

