export interface Episode {
  episode_id: number;
  episode_number: number;
  episode_title: string;
  episode_content: string;
  episode_summary: string;
  characters_featured: Record<string, any>;
  key_events: string[];
  settings: string[];
}

export interface StoryResponse {
  story_id: number;
  title: string;
}

export interface StoryCreate {
  prompt: string;
  num_episodes: number;
}