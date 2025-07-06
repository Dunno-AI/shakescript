import json
from app.services.ai_service.utilsAI import AIUtils


class AIPrompts:
    def __init__(self) -> None:
        self.utils = AIUtils()

    def METADATA_EXTRACTOR_PROMPT(
        self, cleaned_prompt, num_episodes, metadata_template
    ):
        return f"""
        I want your help to write a episodic professional novel/story which would have {num_episodes} episodes.
        This is my Idea for the story:
        <IDEA>
        {cleaned_prompt}
        </IDEA>
        For that I want that you should extract the following data with care.

        - Title: Suggest a title which expresses the feel and theme of the story.
        - Settings: List locations with vivid descriptions as a dictionary (e.g., {{"Cave": "A deep dark cave where the team assembles"}}).
        - Protagonist: Identify the main character with motivation and fears.
        - Characters: All the characters of the story.
        - Theme: Suggest a guiding theme (e.g., redemption).
        - Story Outline: If the story is short, merge phases but include all 6 also maintain the same order of phases as givendont change the order (Exposition, Inciting Incident, Rising Action, Dilemma, Climax, Denouement, Final Episode).
        - Story Outline Description: Give proper outline of the arc also indicate the introduction of characters settings and any supporting characters.

        IMPORTANT POINTS:
        - There Should be a Proper Begining Which sets the environment for the story and introduces character and
        a proper Ending Arc which concludes the story with a proper ending.
        - Pay special attneion to how the characters are being introduced
        there must be a logical connection or some past history or events related to the character.
        - Equally and accordingly divide The number of episodes to each phase for a smooth pace of the story.
        - Only give the metadata not any other thing.

        Instructions for each phase:
        <INSTRUCTIONS>
        {json.dumps(self.utils.story_phases, indent=2)}
        </INSTRUCTIONS>

        Format as JSON:
        {json.dumps(metadata_template, indent=2)}
        """

    def EPISODE_GENERATION_GENERAL_POINTS(self):
        return """
        GENERAL POINTS:
        - Use Character Snapshot to track arcs and relationships, but shift focus to secondary characters or subplots at least once per episode.
        - When ever introducing a new character, show their backstory and introduce their role in the story.
        - Whenever remove a character, show their departure and the impact on the story properly.
        - Use sensory-rich descriptions and varied dialogue, alternating tone (e.g., tense, reflective, humorous) to keep the style dynamic.
        - Are you skipping days at a time? Summarizing events? Don't do that, add scenes to detail them.
        - Is the story rushing over certain plot points and excessively focusing on others?
        - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
        - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?
        - Characters: Who are the characters in this chapter? What do they mean to each other? What is the situation between them? Is it a conflict? Is there tension? Is there a reason that the characters have been brought together?
        - Development: What are the goals of each character, and do they meet those goals? Do the characters change and exhibit growth? Do the goals of each character change over the story?
        - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
        - Dialogue: Does the dialogue make sense? Is it appropriate given the situation? Does the pacing make sense for the scene E.g: (Is it fast-paced because they're running, or slow-paced because they're having a romantic dinner)? 
        - Disruptions: If the flow of dialogue is disrupted, what is the reason for that disruption? Is it a sense of urgency? What is causing the disruption? How does it affect the dialogue moving forwards? 
        - Fill the episodes with necessary details.

        Don't answer these questions directly, instead make your plot implicitly answer them. (Show, don't tell)
        """

    def EPISODE_GENERATION_PROMPT(
        self,
        metadata,
        episode_number,
        num_episodes,
        current_phase,
        PHASE_INFORMATION,
        general_pts,
        prev_episodes_text,
        chunks_text,
        char_snapshot,
        key_events_summary,
        settings_data,
        episode_info,
    ):
        return f"""
        I want your help in crafting the story titled "{metadata.get('title', 'Untitled Story')}" for engaging narration.
        We are writing a story not a stagecraft drama so dont show scene transitions like "camera focuses to canvas", "Stage is set for forest scene".
        We will now be generating the EPISODE {episode_number} of {num_episodes} (Target: upto 450 words).
        The story is set in diverse environments inspired by
        <SETTINGS>
        {settings_data}
        </SETTINGS>

        Avoid repetitive weather references (e.g., rain) unless critical to the plot. Vary the opening line with actions, dialogue, or unexpected events instead of fixed patterns.

        ---
        CURRENT_PHASE: {current_phase}
        Brief of things that should happen in this phase: {episode_info}
        <PHASE_INFORMATION>
        {PHASE_INFORMATION}
        </PHASE_INFORMATION>

        {general_pts}

        <Previous_Episodes (use sparingly to avoid over-reliance)>
        {prev_episodes_text}
        </Previous_Episodes>
        <Relevant_Context (integrate creatively, not as a template)>
        {chunks_text}
        </Relevant_Context>
        <Character_Snapshot>
        {char_snapshot}
        </Character_Snapshot>
        <Key_Events>
        {key_events_summary}
        </Key_Events>

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_title": "A descriptive, Pronounceable Title",
          "episode_content": "An immersive episode with compelling storytelling and varied style."
        }}
        """

    def EPISODE_DETAIL_EXTRACTION_PROMPT(
        self, episode_number, metadata, title_content_data, chunks_text, char_snapshot
    ):
        return f"""
        I have written episode {episode_number} for the story "{metadata.get('title', 'Untitled Story')}".
        Title:
        {title_content_data['episode_title']}
        Content:
        {title_content_data['episode_content']}

        GUIDELINES:
        - Update all the asked details extract enough information so that I can write the next episode by just reading these.
        - Update Character Snapshot based on content (emotional state, relationships).
        - Identify 1-3 Key Events; tag as 'foundational' if they shift the story significantly, 'character-defining' if they develop a character.
        - Summarize concisely (50-70 words) with vivid language.
        - Assign emotional state reflecting tone.

        Character Snapshot: {char_snapshot}
        Relevant Context: {chunks_text}

        - Output STRICTLY a valid JSON object with NO additional text:
        {{
          "episode_summary": "string",
          "episode_emotional_state": "string",
          "characters_featured": [{{"Name": "string", "Role": "string", "Description": "string", "Relationship": {{"Character_Name": "Relation"}}, "role_active": true, "Emotional_State": "string"}}],
          "Key Events": [{{"event": "string", "tier": "foundational/character-defining/transitional/contextual"}}],
          "Settings": {{"Place": "Description"}}
        }}
        """

    def HINGLISH_PROMPT(self, ep_title, ep_content):
        return f"""
        I want your help in converting one of my story's episode to Hinglish.
        EPISODE TITLE:
        {ep_title}
        EPISODE CONTENT:
        {ep_content}

        GUIDELINES:
        - Convert both the title and episode content to Hinglish.
        - Dont use any english word unless it becomes a necessity.
        - You just have to translate the episode not change it, it should remain the same but in hinglish.
        - Give output in a JSON format dont give any additional text.

        {{
            "episode_title": "string",
            "episode_content": "string",
        }}
        """

    def EPISODE_QUALITY_CHECK_PROMPT(self, metadata, episode):
        return f"""
        Analyze this story episode for quality issues:
        
        STORY TITLE: {metadata.get('title', '')}
        SETTING: {metadata.get('setting', '')}
        EPISODE: {episode.get('episode_content', '')}
        
        Check for:
        1. Alignment with story setting and tone
        2. Character consistency
        3. Engaging narrative
        4. Natural dialogue
        5. Descriptive quality
        
        If there are quality issues, describe them briefly in 1-2 sentences.
        If no quality issues, respond with 'GOOD'.
        """

    def EPISODE_CONSISTENCY_CHECK_PROMPT(self, previous_episode, current_episode):
        return f"""
        Analyze these two consecutive story episodes for narrative consistency. 
        
        PREVIOUS EPISODE: {previous_episode.get('content', previous_episode.get('episode_content', ''))}
        
        CURRENT EPISODE: {current_episode.get('episode_content', '')}
        
        Are there any inconsistencies in:
        1. Character locations
        2. Timeline of events
        3. Character knowledge or information
        4. Plot progression
        
        Return only TRUE if consistent or FALSE if inconsistent.
        """

    def REVIEW_EPISODE_PROMPT(self, prev_context, next_context, episode, episode_number, feedback):
        return f"""
            Refine this episode while maintaining narrative continuity with adjacent episodes:
            
            {prev_context}
            
            CURRENT EPISODE (#{episode_number}): {episode.get('episode_content')}
            
            {next_context}
            
            REFINEMENT INSTRUCTIONS: {feedback}
            
            IMPORTANT: Do NOT change any of the following:
            - The core events that happen in this episode
            - Character locations or who is present
            - Key decisions or discoveries made
            - The timing of events relative to other episodes
            - Don't give out response with statements like "here is you refined statements etc etc" just give refined content cuz when taking out response in text format those statements come along..
            
            Focus on maintaining continuity while applying the specific feedback.
            Apply the refinement instructions to improve writing style, emotional tone, descriptiveness, 
            or dialogue quality - while ensuring smooth narrative flow with adjacent episodes.
            """
