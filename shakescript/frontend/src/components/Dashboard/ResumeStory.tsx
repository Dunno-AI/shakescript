import React, { useState } from 'react';
import { Loader2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import LibraryList from './Library/LibraryList';
import { StoryDetails } from '@/types/story';
import { useStoryContext } from '@/contexts/StoryListContext';

export const ResumeStory: React.FC = () => {
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { incompleteStories, loading } = useStoryContext()

    const setToRefinement = (story: StoryDetails) => {
        navigate(`/dashboard/${story.story_id}/refinement`, { state: { story, isHinglish: false, initialBatch: story.current_episode } });
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
        );
    }
    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-400">
                <AlertTriangle className="w-12 h-12 mb-4" />
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="p-6 bg-[#0A0A0A] min-h-full overflow-y-auto">
            <h1 className="text-3xl font-bold text-zinc-100 mb-8">Continue Your Stories</h1>
            
            {incompleteStories.length > 0 ? (
            <LibraryList Stories={incompleteStories} onSelectStory={setToRefinement} />
            ) : (
                <div className="text-center py-20 bg-zinc-900/50 rounded-lg border border-dashed border-zinc-700">
                    <h2 className="text-xl font-semibold text-zinc-300">No Incomplete Stories</h2>
                    <p className="text-zinc-500 mt-2">You've completed all your stories. Ready to start a new one?</p>
                </div>
            )}

        </div>
    );
}; 
