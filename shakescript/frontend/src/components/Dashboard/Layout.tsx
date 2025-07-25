import { useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Story } from './Story';
import { Library } from './Library/Library';
import { ResumeStory } from './ResumeStory';
import UserStats from './UserStats';
import { RefinementRoute } from './RefinementRoute';
import { useAuth } from '../../contexts/AuthContext';

export const Layout = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  if (loading || !user) {
    return <div>Loading...</div>; 
  }

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-white">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<Story />} />
          <Route path="/discover" element={<div>Discover Page</div>} />
          <Route path="/spaces" element={<div>Spaces Page</div>} />
          <Route path="/library" element={<Library />} />
          <Route path="/continue" element={<ResumeStory />} />
          <Route path="/userstats" element={<UserStats />} />
          <Route path="/:storyId/refinement" element={<RefinementRoute />} />
        </Routes>
      </main>
    </div>
  );
};

export default Layout;
