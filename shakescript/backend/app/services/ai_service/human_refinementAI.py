def regenerate_batch(
    self, story_id, episodes, prev_episodes, metadata, feedback_list, auth_id
):
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
                next_context = f"NOTE: This is the final episode of the story and should provide appropriate closure."
            elif episode_number == max(ep.get("episode_number", 0) for ep in episodes):
                next_context = f"NOTE: This is the last episode in the current batch. Future episodes will continue the story."

                # Add story outline context if available
                story_outline = metadata.get("story_outline", [])
                if story_outline and episode_number < len(story_outline):
                    next_outline_point = story_outline[episode_number]
                    next_context += f"\nUPCOMING STORY POINTS: {next_outline_point}"

            refine_prompt = self.prompts.REVIEW_EPISODE_PROMPT(
                prev_context, next_context, episode, episode_number, feedback
            )

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
            refined_episodes.append(episode)

    return refined_episodes


def generate_episode_title(self, episode_content):
    """
    Generate a title for an episode based on its content.
    """
    title_prompt = f"""
    Create a brief, engaging title for this story episode:
    
    {episode_content}...
    
    Title (in 2-6 words):
    """

    title = self.call_llm(title_prompt, max_tokens=20, temperature=0.7)
    return title.strip()
