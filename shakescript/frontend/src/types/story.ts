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

export interface Story {
  story_id: number;
  title: string;
  is_completed: boolean;
  genre: string;
}

export interface Character {
  Name: string;
  Role: string;
  Description: string;
  Relationship: Record<string, any>;
  role_active: boolean;
}

export interface StoryDetails {
  story_id: number;
  title: string;
  setting: string[];
  characters: Record<string, Character>;
  special_instructions: string;
  story_outline: Record<string, string>;
  current_episode: number;
  episodes: {
  id: number;
  number: number;
  title: string;
  content: string;
  summary: string;
}[];
  summary: string;
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
