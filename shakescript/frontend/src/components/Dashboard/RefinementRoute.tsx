import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Refinement } from './Refinement/Refinement';
import { useStoryContext } from '@/contexts/StoryListContext';

export const RefinementRoute = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { completeStory } = useStoryContext();

  const { story, isHinglish, initialBatch } = location.state || {};

  useEffect(() => {
    if (!story) {
      console.error("RefinementRoute: No story data found in location state. Redirecting to dashboard.");
      navigate('/dashboard', { replace: true });
    }
  }, [story, navigate]);

  const handleComplete = () => {
    if (story) {
      completeStory(story.story_id);
      navigate('/dashboard/library');
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  if (!story) {
    return null;
  }

  return (
    <Refinement
      story={story}
      isHinglish={isHinglish || false}
      initialBatch={initialBatch}
      onComplete={handleComplete}
      onBack={handleBack}
    />
  );
};
