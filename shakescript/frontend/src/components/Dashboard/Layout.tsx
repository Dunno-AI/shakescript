import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Story } from './Story';
import { Library } from './Library/Library';
import { ResumeStory } from './ResumeStory';

export const Layout = () => {
  const location = useLocation();
  const path = location.pathname;
  const isMainDashboard = path === '/dashboard' || path === '/dashboard/';

  return (
    <div className="flex h-screen bg-[#0A0A0A] text-white">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        {isMainDashboard && (
          <Story />
        )}
        
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/discover" element={<div>Discover Page</div>} />
          <Route path="/spaces" element={<div>Spaces Page</div>} />
          <Route path="/library" element={<Library />} />
          <Route path="/continue" element={<ResumeStory />} />
        </Routes>
      </main>
    </div>
  );
};
