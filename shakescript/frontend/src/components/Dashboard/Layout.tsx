import { useEffect, useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Story } from './Story';
import { Library } from './Library/Library';
import { ResumeStory } from './ResumeStory';
import UserStats from './UserStats';
import { RefinementRoute } from './RefinementRoute';
import { useAuth } from '../../contexts/AuthContext';
import { StoryPrompt } from './StoryPrompt'; 
import { DashboardProvider } from '../../contexts/DashboardContext';

export const Layout = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [showStoryPrompt, setShowStoryPrompt] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  if (loading || !user) {
    return <div className="flex h-screen w-full items-center justify-center bg-black">Loading Dashboard...</div>;
  }

  return (
    <DashboardProvider>
    <div className="flex h-screen bg-[#0A0A0A] text-white">
      <Sidebar />
      
      <main className="flex-1 flex flex-col overflow-y-auto">
        <Routes>
          {/* Pass the function to open the modal to the main Story page */}
          <Route path="/" element={<Story onNewThreadClick={() => setShowStoryPrompt(true)} />} />
          <Route path="/library" element={<Library />} />
          <Route path="/continue" element={<ResumeStory />} />
          <Route path="/userstats" element={<UserStats />} />
          <Route path="/:storyId/refinement" element={<RefinementRoute />} />
        </Routes>
      </main>

      {/* The modal is now rendered here, outside the Routes, preventing overlap */}
      {showStoryPrompt && (
        <StoryPrompt onClose={() => setShowStoryPrompt(false)} />
      )}
    </div>
    </DashboardProvider>
  );
};

export default Layout;
