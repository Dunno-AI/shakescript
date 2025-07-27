export interface Episode {
  episode_id: number;
  episode_number: number;
  episode_title: string;
  episode_content: string;
  episode_summary: string;
}

export interface StoryResponse {
  story_id: number;
  title: string;
}

export interface StoryCreate {
  prompt: string;
  num_episodes: number;
}

export interface Story {
  story_id: number;
  title: string;
  is_completed: boolean;
  genre: string;
}

export interface StoryDetails {
  story_id: number;
  title: string;
  current_episode: number;
  total_episodes: number;
  episodes: Episode[];
  summary: string;
  batch_size: number;
  refinement_method: "AI" | "HUMAN";
}

export interface StoryCache {
  data: Story[];
  timestamp: number;
}

export interface StoryDetailsCache {
  [key: number]: {
    data: StoryDetails;
    timestamp: number;
  };
}
