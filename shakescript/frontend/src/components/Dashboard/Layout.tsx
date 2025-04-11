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

  const handleStorySubmit = async (prompt: string, episodes: number, isHinglish: boolean, refineMethod: 'human' | 'ai', batchSize: number) => {
    setIsGenerating(true);
    try {
      // First API call to create story
      const createStoryResponse = await axios.post<{ status: string; story: StoryResponse; message: string }>(
        'http://localhost:8000/api/v1/stories/',
        {
          prompt: prompt,
          num_episodes: episodes,
          is_hinglish: isHinglish
        }
      );

      if (!createStoryResponse.data.story || !createStoryResponse.data.story.story_id) {
        throw new Error('No story ID received from create story response');
      }

      // Second API call to generate episodes
      const episodesResponse = await axios.post<Episode[]>(
        `http://localhost:8000/api/v1/episodes/${createStoryResponse.data.story.story_id}/generate`,
        {},
        {
          params: {
            hinglish: isHinglish,
            all: true,
            method: refineMethod,
            batch_size: batchSize
          }
        }
      );

      setCurrentStory({
        title: createStoryResponse.data.story.title,
        episodes: episodesResponse.data,
      });
    } catch (error) {
      console.error('Error generating story:', error);
      if (axios.isAxiosError(error)) {
        console.error('Response data:', error.response?.data);
      }
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