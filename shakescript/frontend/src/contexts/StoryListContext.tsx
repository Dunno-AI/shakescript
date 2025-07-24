import React, { createContext, useState, useContext, useEffect } from "react";
import axios from "axios";
import { Story } from "@/types/story";

const CACHE_DURATION = 6 * 60 * 1000;

interface StoryContextType {
  completedStories: Story[];
  incompleteStories: Story[];
  loading: boolean;
  refreshStories: () => Promise<void>;
  addStory: (story: Story) => void;
  deleteStory: (storyId: number) => Promise<void>;
  completeStory: (storyId: number) => void;
}

const StoryContext = createContext<StoryContextType | undefined>(undefined);

export const StoryProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [completedStories, setCompletedStories] = useState<Story[]>([]);
  const [incompleteStories, setIncompleteStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [cacheTimestamp, setCacheTimestamp] = useState<number | null>(null);
  const BASE_URL = import.meta.env.VITE_BACKEND_URL;

  const fetchStories = async () => {
    setLoading(true);
    try {
      const res = await axios.get(BASE_URL + "/api/v1/stories/all");
      const allStories = res.data.stories;
      const completed = allStories.filter((s: any) => s.is_completed);
      const incomplete = allStories.filter((s: any) => !s.is_completed);
      setCompletedStories(completed);
      setIncompleteStories(incomplete);
      setCacheTimestamp(Date.now());
    } catch (err) {
      console.error("Failed fetching stories", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshStories = async () => {
    await fetchStories();
  };

  const addStory = (story: Story) => {
    if(!story.is_completed){
      setIncompleteStories((prev) => [story, ...prev]);
    }
    else{
      setIncompleteStories(prev => prev.filter(s => s.story_id !== story.story_id));
      setCompletedStories(prev => [story, ...prev]);
    }
  };

  const completeStory = (storyId: number) => {
    const completedStory: Story | undefined = incompleteStories.find((s) => s.story_id === storyId);
    if(completedStory)
      setCompletedStories((prev) => [completedStory, ...prev]);
    setIncompleteStories((prev) => prev.filter((s) => s.story_id !== storyId));
  }

  const deleteStory = async (storyId: number) => {
    try {
      await fetch(`${BASE_URL}/api/v1/stories/${storyId}`, {
        method: "DELETE",
      });
      setCompletedStories((prev) => prev.filter((s) => s.story_id !== storyId));
      setIncompleteStories((prev) => prev.filter((s) => s.story_id !== storyId));
    } catch (err) {
      console.error("Failed to delete story", err);
      throw err;
    }
  };

  useEffect(() => {
    if (cacheTimestamp && Date.now() - cacheTimestamp < CACHE_DURATION) {
      setLoading(false);
    } else {
      fetchStories();
    }
  }, []);

  return (
    <StoryContext.Provider
      value={{
        completedStories,
        incompleteStories,
        loading,
        refreshStories,
        addStory,
        deleteStory,
        completeStory
      }}
    >
      {children}
    </StoryContext.Provider>
  );
};

export const useStoryContext = (): StoryContextType => {
  const context = useContext(StoryContext);
  if (!context) {
    throw new Error("useStoryContext must be used within a StoryProvider");
  }
  return context;
};
