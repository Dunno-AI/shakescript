import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Refinement } from './Refinement';
import { Loader2, AlertTriangle, PlayCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface StorySummary {
  story_id: number;
  title: string;
  is_completed: boolean;
  genre: string;
  num_episodes: number;
  validated_episodes: number;
}

interface StoryDetail extends StorySummary {
  prompt: string;
  batch_size: number;
  refinement: 'HUMAN' | 'AI';
  is_hinglish: boolean;
  episodes: any[];
}

interface SelectedStory {
    storyId: number;
    totalEpisodes: number;
    batchSize: number;
    refinementType: 'human' | 'ai';
    isHinglish: boolean;
    initialBatch: number;
}

export const ResumeStory: React.FC = () => {
    const [incompleteStories, setIncompleteStories] = useState<StorySummary[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedStory, setSelectedStory] = useState<SelectedStory | null>(null);
    const navigate = useNavigate();
    const BASE_URL = import.meta.env.VITE_BACKEND_URL;

    const fetchIncompleteStories = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get<{ stories: StorySummary[] }>(`${BASE_URL}/api/v1/stories/all`);
            const incomplete = response.data.stories.filter(story => !story.is_completed);
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
            const detailResponse = await axios.get<{ story: StoryDetail }>(`${BASE_URL}/api/v1/stories/${storyId}`);
            const story = detailResponse.data.story;
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
        <div className="p-6 bg-[#181818] min-h-full">
            <h1 className="text-3xl font-bold text-zinc-100 mb-8">Continue Your Stories</h1>
            
            {incompleteStories.length > 0 ? (
                <div className="space-y-4">
                    {incompleteStories.map(story => {
                        const progress = story.num_episodes > 0 ? (story.validated_episodes / story.num_episodes) * 100 : 0;
                        // Use batch_size if present, otherwise default to 1
                        const batchSize = (story as any).batch_size || 1;
                        const initialBatch = Math.floor((story.validated_episodes || 0) / batchSize) + 1;
                        return (
                            <div key={story.story_id} className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex items-center justify-between hover:bg-zinc-800/50 transition-colors duration-200">
                                <div className="flex-1">
                                    <h2 className="text-lg font-semibold text-zinc-200">{story.title || 'Untitled Story'}</h2>
                                    <p className="text-sm text-zinc-400 capitalize">{story.genre || 'N/A'}</p>
                                    <div className="mt-3 flex items-center gap-4">
                                        <div className="w-full bg-zinc-700 rounded-full h-2 flex-1">
                                            <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
                                        </div>
                                        <p className="text-xs text-zinc-400 font-mono">{story.validated_episodes} / {story.num_episodes}</p>
                                    </div>
                                    <p className="text-xs text-zinc-500 mt-1">
                                      Resumes from batch {initialBatch}
                                    </p>
                                </div>
                                <button
                                    onClick={() => handleResume(story.story_id)}
                                    className="ml-6 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
                                >
                                    <PlayCircle size={18} />
                                    <span>Continue</span>
                                </button>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="text-center py-20 bg-zinc-900/50 rounded-lg border border-dashed border-zinc-700">
                    <h2 className="text-xl font-semibold text-zinc-300">No Incomplete Stories</h2>
                    <p className="text-zinc-500 mt-2">You've completed all your stories. Ready to start a new one?</p>
                </div>
            )}

            {selectedStory && (
                <Refinement
                    storyId={selectedStory.storyId}
                    totalEpisodes={selectedStory.totalEpisodes}
                    batchSize={selectedStory.batchSize}
                    refinementType={selectedStory.refinementType}
                    isHinglish={selectedStory.isHinglish}
                    initialBatch={selectedStory.initialBatch}
                    onComplete={handleRefinementComplete}
                    onClose={handleRefinementClose}
                />
            )}
        </div>
    );
}; 
