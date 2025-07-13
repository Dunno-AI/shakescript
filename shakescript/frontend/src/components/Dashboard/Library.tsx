import { useState } from 'react';
import LibraryList from './LibraryList';
import StoryReader from './StoryReader';
import { StoryDetails } from '@/types/story';

export const Library = () => {
  const [selectedStory, setSelectedStory] = useState<StoryDetails | null>(null);

  return (
    <div className="flex-1 bg-[#0A0A0A] p-8 overflow-y-auto">
      {!selectedStory ? (
        <LibraryList onSelectStory={setSelectedStory} />
      ) : (
        <StoryReader story={selectedStory} onBack={() => setSelectedStory(null)} />
      )}
    </div>
  );
};

