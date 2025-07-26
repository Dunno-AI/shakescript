// src/types/story.ts

export interface Episode {
  id: number;
  number: number;
  title: string;
  content: string;
  summary: string;
  emotional_state: string;
  key_events: any[];
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
