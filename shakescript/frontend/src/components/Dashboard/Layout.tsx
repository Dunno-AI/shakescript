import { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Story } from './Story';
import { Library } from './Library';
import axios from 'axios';
import { Episode, StoryResponse } from '../../types/story';

export const Layout = () => {
  const location = useLocation();
  const path = location.pathname;
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStory, setCurrentStory] = useState<{ title?: string; episodes: Episode[] }>({
    episodes: []
  });
  
  const isMainDashboard = path === '/dashboard' || path === '/dashboard/';

  const handleStorySubmit = async (prompt: string, episodes: number, isHinglish: boolean) => {
    setIsGenerating(true);
    try {
      // First API call to create story
      const createStoryResponse = await axios.post<StoryResponse>(
        'http://localhost:8000/api/v1/stories/',
        {
          prompt,
          num_episodes: episodes,
          is_hinglish: isHinglish
        }
      );

      // Second API call to generate episodes
      const episodesResponse = await axios.post<Episode[]>(
        `http://localhost:8000/api/v1/episodes/${createStoryResponse.data.story_id}/generate`,
        null,
        {
          params: {
            all: true
          }
        }
      );

      setCurrentStory({
        title: createStoryResponse.data.title,
        episodes: episodesResponse.data,
      });
    } catch (error) {
      console.error('Error generating story:', error);
      // TODO: Add error handling UI
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-white">
      <Sidebar onSubmit={handleStorySubmit} isGenerating={isGenerating} />
      <main className="flex-1 flex flex-col">
        {isMainDashboard && (
          <Story 
            story={currentStory}
            isGenerating={isGenerating}
          />
        )}
        
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          {/* <Route path="/story" element={<Story />} /> */}
          <Route path="/discover" element={<div>Discover Page</div>} />
          <Route path="/spaces" element={<div>Spaces Page</div>} />
          <Route path="/library" element={<Library />} />
        </Routes>
      </main>
    </div>
  );
};