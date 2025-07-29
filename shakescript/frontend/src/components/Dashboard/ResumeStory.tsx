import React, { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { SpinLoading } from 'respinner';
import { useNavigate } from 'react-router-dom';
import LibraryList from './Library/LibraryList';
import { useStoryContext } from '@/contexts/StoryListContext';
import { StoryDetails } from '@/types/story';

export const ResumeStory: React.FC = () => {
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { incompleteStories, loading } = useStoryContext();

    const setToRefinement = (story: StoryDetails) => {
        try {
            const initialBatch = Math.floor((story.episodes.length) / (story.batch_size || 1)) + 1;
            navigate(`/dashboard/${story.story_id}/refinement`, {
                state: {
                    story: { ...story, total_episodes: story.total_episodes },
                    isHinglish: false, 
                    initialBatch,
                }
            });
        } catch (err) {
            setError(`Failed to process story details for story ${story.story_id}.`);
            console.error(err);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full space-y-3">
                <SpinLoading fill="#777" borderRadius={4} count={12} />
                <p className="text-xs text-zinc-500">Loading stories</p>
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
