import React, { useState, useEffect } from 'react';
import { useAuthFetch } from '../../lib/utils';
import { Refinement } from './Refinement';
import { Loader2, AlertTriangle, PlayCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import LibraryList from './Library/LibraryList';
import { StoryDetails } from '@/types/story';
import { useStoryContext } from '@/contexts/StoryListContext';

export const ResumeStory: React.FC = () => {
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const BASE_URL = import.meta.env.VITE_BACKEND_URL;
    const authFetch = useAuthFetch();

    const fetchIncompleteStories = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await authFetch(`${BASE_URL}/api/v1/stories/all`);
            const response = await res.json();
            const incomplete = response.stories.filter((story: any) => !story.is_completed);
            setIncompleteStories(incomplete);
        } catch (err) {
            setError('Failed to fetch stories. Please try again later.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchIncompleteStories();
    }, []);

    const handleResume = async (storyId: number) => {
        try {
            const res = await authFetch(`${BASE_URL}/api/v1/stories/${storyId}`);
            const detailResponse = await res.json();
            const story = detailResponse.story;
            // Calculate initial batch: (validated_episodes / batch_size) + 1
            const initialBatch = Math.floor((story.validated_episodes || 0) / (story.batch_size || 1)) + 1;
            setSelectedStory({
                storyId: story.story_id,
                totalEpisodes: story.num_episodes,
                batchSize: story.batch_size, // always use batch_size from detail
                refinementType: story.refinement === 'HUMAN' ? 'human' : 'ai',
                isHinglish: story.is_hinglish,
                initialBatch,
            });
        } catch (err) {
            setError(`Failed to fetch story details for story ${storyId}.`);
            console.error(err);
        }
    };
    
    const handleRefinementComplete = () => {
        setSelectedStory(null);
        fetchIncompleteStories(); // Refetch to update the list
    };

    const handleRefinementClose = () => {
        setSelectedStory(null);
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
