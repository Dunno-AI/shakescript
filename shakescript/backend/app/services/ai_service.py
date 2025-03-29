import google.generativeai as genai
from openai import OpenAI
from app.core.config import settings
from app.utils import extract_json_manually, parse_user_prompt
from app.services.embedding_service import EmbeddingService  # For chunks
from typing import Dict, List
import json
import re


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()  # For retrieving chunks

    def extract_metadata(self, user_prompt: str) -> Dict:
        """Extract story metadata from user prompt using Gemini."""

        #Preprocess the prompt to normalize 
        cleaned_prompt = parse_user_prompt(user_prompt)
        instruction = """
    Extract structured metadata from the following story prompt and return it as valid JSON.
    - Title: Suggest a concise, pronounceable title (e.g., avoid silent letters or odd spellings).
    - Settings: Identify locations with brief, vivid descriptions and add phonetic pronunciation for each place.
    - Characters: List key entities with roles, descriptions, and phonetic pronunciation for names (e.g., 'Lee-lah' for Lila).
    - Special Instructions: Include a narration tone (e.g., suspenseful, calm) for audio delivery.
    Format EXACTLY as follows:
    {
      "Title": "string",
      "Settings": [{"Place": "string", "Description": "string", "Pronunciation": "string"}],
      "Characters": {
        "Name": {
          "Name": "string",
          "Role": "string",
          "Description": "string",
          "Relationship": {"Character_Name": "Relation"},
          "Pronunciation": "string"
        }
      },
      "Special Instructions": "string (include tone: e.g., suspenseful, cheerful)",
      "Story Outline": {"Episode X-Y (Phase)": "Description"}
    }
    IMPORTANT: Use simple, pronounceable names and terms for TTS compatibility.
        """
        prompt = f"{instruction}\n\nUser Prompt: {cleaned_prompt}"
        response = self.model.generate_content(prompt)
        raw_text = response.text

        if "```json" in raw_text or "```" in raw_text:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, raw_text, re.DOTALL)
            if matches:
                raw_text = matches[0]

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return extract_json_manually(raw_text)

    def _parse_episode_response(self, response_text: str, metadata: Dict) -> Dict:
        """Adopted from Colab's Shakyscript.ipynb - lightweight and robust parsing."""
        try:
            episode_data = json.loads(response_text)
            return episode_data
        except json.JSONDecodeError:
            json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            if matches:
                try:
                    episode_data = json.loads(matches[0])
                    return episode_data
                except:
                    cleaned_text = matches[0].replace("'", '"')
                    try:
                        episode_data = json.loads(cleaned_text)
                        return episode_data
                    except:
                        pass

            json_pattern2 = r'{[\s\S]*"episode_title"[\s\S]*"episode_content"[\s\S]*}'
            match = re.search(json_pattern2, response_text)
            if match:
                try:
                    cleaned_json = match.group(0).replace("'", '"')
                    episode_data = json.loads(cleaned_json)
                    return episode_data
                except:
                    pass

            title_match = re.search(r'"episode_title":\s*"([^"]+)"', response_text)
            content_match = re.search(
                r'"episode_content":\s*"([^"]*(?:(?:"[^"]*)*[^"])*)"', response_text
            )
            summary_match = re.search(r'"episode_summary":\s*"([^"]+)"', response_text)

            episode_title = (
                title_match.group(1)
                if title_match
                else f"Episode {metadata.get('current_episode', 1)}"
            )
            episode_content = content_match.group(1) if content_match else response_text
            episode_summary = (
                summary_match.group(1)
                if summary_match
                else "Episode summary not available."
            )

            return {
                "episode_title": episode_title,
                "episode_content": episode_content,
                "episode_summary": episode_summary,  # Included as fallback, but not required in prompt
            }

    def generate_episode_helper(
        self,
        num_episodes: int,
        metadata: Dict,
        episode_number: int,
        char_text: str,
        story_id: int,
        prev_episodes: List = None,
    ) -> Dict:
        """Generate a structured and well-curated episode with clear progression from intro to conclusion."""

        # Extract settings with proper formatting
        settings_data = (
            "\n".join(
                f"Place: {s.get('Place', 'Unknown')}, Description: {s.get('Description', 'No description')}"
                for s in metadata.get("Settings", [])
                if isinstance(s, dict)
            )
            or "No settings provided."
        )

        # Fetch last 3 episode summaries for continuity
        prev_episodes_text = (
            "\n\n".join(
                f"EPISODE {ep_num} SUMMARY: {summary}\nEPISODE {ep_num} CONTENT: {content}"
                for ep_num, content, summary in prev_episodes[-3:]  # Last 3 episodes
            )
            if prev_episodes
            else ""
        )

        # Retrieve top 3 relevant chunks
        chunks_text = (
            "\n\n".join(
                f"RELEVANT CONTEXT: {chunk['content']}"
                for chunk in self.embedding_service.retrieve_relevant_chunks(
                    story_id, prev_episodes_text or char_text, k=3
                )
            )
            or ""
        )

        # Extract active characters with descriptions
        characters = json.loads(char_text) if char_text else {}
        char_snapshot = (
            "\n".join(
                f"{char['Name']}: {char['Description'][:50]}{'...' if len(char['Description']) > 50 else ''}"
                for char in characters.values()
                if char.get("role_active", True)
            )
            or "No active characters yet."
        )

        # **Simplified Phase Selection Logic** (Removed unnecessary thresholds)
        if num_episodes == 1:
            phase = "ONE-SHOT STORY: Merge all phases into a single episode."
        elif episode_number == num_episodes:  # ✅ FINAL EPISODE - FORCED CLOSURE
            phase = """
            FINAL RESOLUTION:
            - This is the **LAST episode**. ALL conflicts MUST be resolved.
            - Ensure that **all character arcs conclude definitively** (success, failure, sacrifice, or transformation).
            - **No cliffhangers. No unresolved mysteries.**
            - The **main antagonist must be defeated, neutralized, or fully resolved**.
            - Any prophecy, curse, or mystery **must be answered fully**.
            - The ending should feel **final** (happy, tragic, or bittersweet), with a lasting impact.
            """
        elif episode_number == num_episodes - 1:
            phase = "FALLING ACTION: Wrapping up loose threads, preparing for final resolution."
        elif episode_number == 1:
            phase = "INTRODUCTION: Establish setting, introduce main characters, and present initial conflict."
        elif episode_number <= num_episodes * 0.4:
            phase = "BUILDING ACTION: Develop subplots, introduce obstacles, and raise stakes."
        elif episode_number <= num_episodes * 0.8:
            phase = "CLIMAX: Key confrontations occur, major events shift the direction of the story."
        else:
            phase = "BUILDING ACTION"  # Fallback

        # ✅ **Professional & Efficient Prompt Structure**

        instruction = f"""
        You are crafting a structured, immersive story titled "{metadata.get('title', 'Untitled Story')}" designed for engaging narration.

        **📌 Episode {episode_number} of {num_episodes} (Target: 300-400 words).**  
        Set in **"{settings_data}"**, this episode must maintain a gripping flow, with a clear beginning, middle, and end.

        ---

### **🚀 Storytelling Rules for a Stronger Narrative:**
        1️⃣ **Deep Story Consistency & Character Growth:**  
           - Maintain logical progression from previous episodes.  
           - Ensure **consistent character arcs** (strengths, weaknesses, motivations).  
           - Make **every action meaningful**—no filler dialogue or unnecessary exposition.  

        2️⃣ **Stronger Narrative Phases for Engagement:**  
           **Phase:** {phase}  
           - **Introduction (Ep 1):** Establish the world, key characters, and initial mystery.  
           - **Rising Action (Ep 2 - {int(num_episodes * 0.4)}):** Increase stakes through unexpected challenges.  
           - **Climax (Ep {int(num_episodes * 0.5)} - {int(num_episodes * 0.8)}):** Major confrontations, twists, and revelations.  
           - **Falling Action (Ep {num_episodes - 1}):** Start resolving subplots, prepare for the conclusion.  
           - **Final Resolution (Ep {num_episodes}):** **All conflicts MUST be resolved** (no cliffhangers).  

        3️⃣ **Enhance Immersion & Atmosphere:**  
           - Use **vivid sensory details** to immerse the reader (sounds, textures, emotions).  
           - Increase **psychological tension** through **character thoughts, shifting environments, and mind games.**  
           - Every episode should **advance the overall mystery & deepen the stakes.**  

        4️⃣ **Diverse Threats & Challenges:**  
           Avoid repetitive encounters. Integrate:  
           - **Physical Threats:** Shadows, monsters, environmental hazards.  
           - **Psychological Horror:** Unreliable memories, illusions, betrayals.  
           - **Emotional Conflict:** Character-driven tension, moral dilemmas, inner fears.  

        ---

### **📜 Your Task: Generate a Well-Paced Episode**
        1. **Use prior episodes & context below to ensure coherence.**  
        2. **Prioritize character-driven storytelling & emotional depth.**  
        3. **Weave in foreshadowing for upcoming twists.**  

        🔹 **Previous Episodes Recap:**  
        {prev_episodes_text}  

        🔹 **Relevant Context (Extracted from Past Episodes):**  
        {chunks_text}  

        🔹 **Active Characters & Their Current Motivations:**  
        {char_snapshot}  

        **📢 Output ONLY a valid JSON response in this format:**  
        {{
          "episode_title": "A Short, Pronounceable Title",
          "episode_content": "A well-structured, immersive episode with compelling storytelling.",
          "episode_summary": "A concise 50-70 word summary of the episode’s key events and outcomes.
        }}
        """
           # ╭──────────────╮
           # │ gemini model │
           # ╰──────────────╯
        response = self.model.generate_content(instruction)
        raw_text = response.text
        return self._parse_episode_response(raw_text, metadata)

        # ✅ **Call OpenAI's GPT-4o API using self.openai_client**

        # response = self.openai_client.chat.completions.create(
        # model="gpt-4o",
        # messages=[
        # {"role": "system", "content": "You are a professional storyteller creating structured, well-paced narratives."},
        # {"role": "user", "content": instruction}
        # ],
        # temperature=0.7,
        # max_tokens=1000
        # )

        # raw_text = response.choices[0].message.content or ""
        # return self._parse_episode_response(raw_text, metadata)
