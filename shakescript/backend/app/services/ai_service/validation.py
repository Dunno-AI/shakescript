from typing import Dict, List, Any, Optional
import re


def validate_batch(self, story_id, episodes, prev_episodes, metadata):
    """
    Validate a batch of episodes for narrative consistency and quality.
    """
    validation_issues = []

    for i, episode in enumerate(episodes):
        if prev_episodes and i == 0:
            if not self.is_consistent_with_previous(episode, prev_episodes[-1]):
                validation_issues.append(
                    {
                        "episode_number": episode["episode_number"],
                        "feedback": "Ensure this episode follows directly from the previous one in the timeline",
                    }
                )

        if i > 0 and not self.is_consistent_with_previous(episode, episodes[i - 1]):
            validation_issues.append(
                {
                    "episode_number": episode["episode_number"],
                    "feedback": "Ensure this episode maintains continuity with the previous episode",
                }
            )

        quality_feedback = self.check_episode_quality(episode, metadata)
        if quality_feedback:
            validation_issues.append(
                {
                    "episode_number": episode["episode_number"],
                    "feedback": quality_feedback,
                }
            )

    if validation_issues:
        return {
            "status": "needs_refinement",
            "episodes": episodes,
            "feedback": validation_issues,
        }

    return {"status": "success", "episodes": episodes}


def is_consistent_with_previous(self, current_episode, previous_episode):
    """
    Check if the current episode is consistent with the previous episode.
    This uses AI to analyze narrative continuity between episodes.
    """
    consistency_prompt = f"""
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

    response = self.call_llm(consistency_prompt, max_tokens=10, temperature=0.1)
    return "TRUE" in response.upper()


def check_episode_quality(self, episode, metadata):
    """
    Check the quality of an episode based on story metadata.
    Returns feedback if quality issues are found, otherwise returns None.
    """
    # Create a prompt for checking quality
    quality_prompt = f"""
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

    response = self.call_llm(quality_prompt, max_tokens=100, temperature=0.3)
    return None if "GOOD" in response.upper() else response.strip()


def regenerate_batch(self, story_id, episodes, prev_episodes, metadata, feedback_list):
    """
    Regenerate episodes with feedback while preserving core narrative elements
    and ensuring continuity between episodes within the current batch,
    handling edge cases like first/last episodes properly.
    """

    feedback_by_episode = {fb["episode_number"]: fb["feedback"] for fb in feedback_list}

    episodes_map = {ep.get("episode_number"): ep for ep in episodes}

    total_episodes = metadata.get("num_episodes", 0)

    refined_episodes = []
    for episode in episodes:
        episode_number = episode.get("episode_number")

        if episode_number in feedback_by_episode:
            feedback = feedback_by_episode[episode_number]

            prev_in_batch = episodes_map.get(episode_number - 1)
            next_in_batch = episodes_map.get(episode_number + 1)

            prev_context = ""
            if prev_in_batch:
                prev_context = f"PREVIOUS EPISODE IN BATCH (#{prev_in_batch.get('episode_number')}): {prev_in_batch.get('episode_content')}"
            elif prev_episodes and episode_number > 1:

                for prev_ep in reversed(prev_episodes):
                    prev_ep_num = prev_ep.get("episode_number", 0)
                    if prev_ep_num == episode_number - 1:
                        prev_context = f"PREVIOUS EPISODE (#{prev_ep_num}): {prev_ep.get('content', prev_ep.get('episode_content', ''))}"
                        break

            if episode_number == 1:

                characters = metadata.get("characters", [])
                character_names = []
                for char in characters:
                    if isinstance(char, dict) and "Name" in char:
                        character_names.append(char["Name"])

                prev_context = f"""
                STORY BEGINNING CONTEXT:
                Title: {metadata.get('title', '')}
                Setting: {metadata.get('setting', '')}
                Main Characters: {', '.join(character_names)}
                """

            next_context = ""
            if next_in_batch:
                next_context = f"NEXT EPISODE IN BATCH (#{next_in_batch.get('episode_number')}): {next_in_batch.get('episode_content')}"
            elif episode_number == total_episodes:
                # If this is the final episode of the story
                next_context = f"NOTE: This is the final episode of the story and should provide appropriate closure."
            elif episode_number == max(ep.get("episode_number", 0) for ep in episodes):
                # If this is the last episode in the batch but not the final episode
                next_context = f"NOTE: This is the last episode in the current batch. Future episodes will continue the story."

                # Add story outline context if available
                story_outline = metadata.get("story_outline", [])
                if story_outline and episode_number < len(story_outline):
                    next_outline_point = story_outline[episode_number]
                    next_context += f"\nUPCOMING STORY POINTS: {next_outline_point}"

            refine_prompt = f"""
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

            # Call AI to refine with the more specific prompt
            refined_content = self.call_llm(
                refine_prompt, max_tokens=2000, temperature=0.7
            )

            # Create refined episode while preserving other metadata
            refined_episode = episode.copy()
            refined_episode["episode_content"] = refined_content
            if "title" in feedback.lower():
                refined_episode["episode_title"] = self.generate_episode_title(
                    refined_content
                )

            refined_episodes.append(refined_episode)
        else:
            # No feedback for this episode, keep it as is
            refined_episodes.append(episode)

    return refined_episodes


def generate_episode_title(self, episode_content):
    """
    Generate a title for an episode based on its content.
    """
    title_prompt = f"""
    Create a brief, engaging title for this story episode:
    
    {episode_content[:500]}...
    
    Title (in 2-6 words):
    """

    title = self.call_llm(title_prompt, max_tokens=20, temperature=0.7)
    return title.strip()
