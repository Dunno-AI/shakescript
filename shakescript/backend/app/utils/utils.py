import re
import json
from typing import Dict


def clean_json_text(text: str) -> str:
    """
    Preprocess raw text to make it more JSON-friendly before parsing.
    Removes code blocks, fixes single quotes, and handles trailing commas.

    Args:
        text (str): Raw text from an AI response.
    Returns:
        str: Cleaned text ready for json.loads().
    """
    # Remove markdown code blocks (e.g., ```json ... ```)
    text = re.sub(r"```(?:json)?\s*\n(.*?)\n```", r"\1", text, flags=re.DOTALL)
    # Replace single quotes with double quotes for valid JSON
    text = text.replace("'", '"')
    # Remove trailing commas before closing brackets/braces
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def extract_json_manually(text: str) -> Dict:
    """
    Manually extract JSON-like data from a string when json.loads() fails.
    Uses regex to find key-value pairs and builds a metadata dict.
    Adapted to match StoryResponse schema from schemas.py.

    Args:
        text (str): Raw text from an AI response.
    Returns:
        Dict: Extracted metadata with default values for missing fields.
    """
    # Default metadata structure based on your StoryResponse schema
    metadata = {
        "Title": "Untitled Story",
        "Settings": [],  # List of {"Place": "Description"} dicts
        "Characters": {},  # Dict of character objects
        "Special Instructions": "",
        "Story Outline": {},  # Dict of episode outlines
    }

    # Extract Title
    title_match = re.search(r'"Title":\s*"([^"]+)"', text)
    if title_match:
        metadata["Title"] = title_match.group(1)

    # Extract Settings (list of dicts)
    settings_match = re.search(r'"Settings":\s*(\[.*?\])', text, re.DOTALL)
    if settings_match:
        try:
            settings_text = settings_match.group(1).replace("'", '"')
            metadata["Settings"] = json.loads(settings_text)
        except:
            # Fallback: Extract individual "Place": "Description" pairs
            settings_text = settings_match.group(1)
            place_desc_pairs = re.findall(
                r'{"Place":\s*"([^"]+)",\s*"Description":\s*"([^"]+)"}', settings_text
            )
            metadata["Settings"] = [
                {"Place": place, "Description": desc}
                for place, desc in place_desc_pairs
            ]

    # Extract Characters (dict of character objects)
    chars_match = re.search(r'"Characters":\s*({.*?})', text, re.DOTALL)
    if chars_match:
        try:
            chars_text = chars_match.group(1).replace("'", '"')
            metadata["Characters"] = json.loads(chars_text)
        except:
            # Fallback: Extract character names and basic details
            chars_text = chars_match.group(1)
            char_entries = re.findall(
                r'"([^"]+)":\s*{\s*"Name":\s*"([^"]+)",\s*"Role":\s*"([^"]+)",\s*"Description":\s*"([^"]+)"',
                chars_text,
            )
            metadata["Characters"] = {
                name: {
                    "Name": name,
                    "Role": role,
                    "Description": desc,
                    "Relationship": {},  # Default empty if not parsed
                    "role_active": True,  # Default value
                }
                for _, name, role, desc in char_entries
            }

    # Extract Special Instructions
    special_match = re.search(r'"Special Instructions":\s*"([^"]+)"', text)
    if special_match:
        metadata["Special Instructions"] = special_match.group(1)

    # Extract Story Outline (dict of strings)
    outline_match = re.search(r'"Story Outline":\s*({.*?})', text, re.DOTALL)
    if outline_match:
        try:
            outline_text = outline_match.group(1).replace("'", '"')
            metadata["Story Outline"] = json.loads(outline_text)
        except:
            # Fallback: Extract key-value pairs
            outline_text = outline_match.group(1)
            pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', outline_text)
            metadata["Story Outline"] = dict(pairs)

    return metadata


# Optional: Add a similar function for episode parsing if needed
def extract_episode_json_manually(text: str) -> Dict:
    """
    Manually extract episode data from a string when json.loads() fails.
    Matches EpisodeResponse schema from schemas.py.

    Args:
        text (str): Raw text from an AI response.
    Returns:
        Dict: Extracted episode data with default values.
    """
    episode_data = {
        "episode_title": "Untitled Episode",
        "episode_content": "",
        "episode_summary": "No summary available",
        "characters_featured": {},
        "Key Events": [],
        "Settings": [],
    }

    # Extract episode_title
    title_match = re.search(r'"episode_title":\s*"([^"]+)"', text)
    if title_match:
        episode_data["episode_title"] = title_match.group(1)

    # Extract episode_content
    content_match = re.search(
        r'"episode_content":\s*"([^"]*(?:(?:"[^"]*)*[^"])*)"', text
    )
    if content_match:
        episode_data["episode_content"] = content_match.group(1)

    # Extract episode_summary
    summary_match = re.search(r'"episode_summary":\s*"([^"]+)"', text)
    if summary_match:
        episode_data["episode_summary"] = summary_match.group(1)

    # Extract characters_featured (simplified)
    chars_match = re.search(r'"characters_featured":\s*({.*?})', text, re.DOTALL)
    if chars_match:
        try:
            chars_text = chars_match.group(1).replace("'", '"')
            episode_data["characters_featured"] = json.loads(chars_text)
        except:
            pass  # Keep default empty dict

    # Extract Key Events
    events_match = re.search(r'"Key Events":\s*(\[.*?\])', text, re.DOTALL)
    if events_match:
        try:
            events_text = events_match.group(1).replace("'", '"')
            episode_data["Key Events"] = json.loads(events_text)
        except:
            events_text = events_match.group(1)
            events = re.findall(r'"([^"]+)"', events_text)
            episode_data["Key Events"] = events

    # Extract Settings
    settings_match = re.search(r'"Settings":\s*(\[.*?\])', text, re.DOTALL)
    if settings_match:
        try:
            settings_text = settings_match.group(1).replace("'", '"')
            episode_data["Settings"] = json.loads(settings_text)
        except:
            pass  # Keep default empty list

    return episode_data

