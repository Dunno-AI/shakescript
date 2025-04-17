import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Loader2, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

interface Episode {
  episode_number: number;
  content: string;
  feedback?: string;
}

interface RefinementProps {
  storyId: number;
  totalEpisodes: number;
  batchSize: number;
  refinementType: 'ai' | 'human';
  isHinglish: boolean;
  onComplete: () => void;
  onClose: () => void;
}

export const Refinement: React.FC<RefinementProps> = ({
  storyId,
  totalEpisodes,
  batchSize,
  refinementType,
  isHinglish,
  onComplete,
  onClose
}) => {
  const [currentBatch, setCurrentBatch] = useState(0);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<number, string>>({});
  const [isValidating, setIsValidating] = useState(false);

  const totalBatches = Math.ceil(totalEpisodes / batchSize);
  const currentBatchStart = currentBatch * batchSize + 1;
  const currentBatchEnd = Math.min((currentBatch + 1) * batchSize, totalEpisodes);

  useEffect(() => {
    generateBatch();
  }, [currentBatch]);

  const generateBatch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/episodes/${storyId}/generate-batch`, {
        params: {
          batch_size: batchSize,
          hinglish: isHinglish,
          refinement_type: refinementType
        }
      });
      setEpisodes(response.data.episodes);
    } catch (err) {
      setError('Failed to generate episodes. Please try again.');
      console.error('Error generating episodes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefinement = async () => {
    setIsValidating(true);
    try {
      if (refinementType === 'ai') {
        await axios.post(`http://localhost:8000/api/v1/episodes/${storyId}/validate-batch`);
      } else {
        const feedbackArray = episodes.map(episode => ({
          episode_number: episode.episode_number,
          feedback: feedback[episode.episode_number] || ''
        }));
        await axios.post(`http://localhost:8000/api/v1/episodes/${storyId}/refine-batch`, feedbackArray);
      }

      if (currentBatch < totalBatches - 1) {
        setCurrentBatch(prev => prev + 1);
      } else {
        onComplete();
      }
    } catch (err) {
      setError('Failed to process refinement. Please try again.');
      console.error('Error during refinement:', err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleFeedbackChange = (episodeNumber: number, value: string) => {
    setFeedback(prev => ({
      ...prev,
      [episodeNumber]: value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[#111111] rounded-xl border border-[#2a2a2a] shadow-lg w-full max-w-4xl mx-3 max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-[#2a2a2a]">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-zinc-100">
              Episode Refinement
            </h2>
            <div className="flex items-center gap-4">
              <span className="text-zinc-400 text-sm">
                Batch {currentBatch + 1} of {totalBatches}
              </span>
              <button
                onClick={onClose}
                className="p-1 hover:bg-zinc-800 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5 text-zinc-400" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : error ? (
            <div className="text-red-500 text-center">{error}</div>
          ) : (
            <div className="space-y-6">
              {episodes.map((episode) => (
                <div key={episode.episode_number} className="bg-zinc-900/50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-zinc-100 mb-2">
                    Episode {episode.episode_number}
                  </h3>
                  <div className="prose prose-invert max-w-none mb-4">
                    <p className="text-zinc-400">{episode.content}</p>
                  </div>
                  {refinementType === 'human' && (
                    <textarea
                      value={feedback[episode.episode_number] || ''}
                      onChange={(e) => handleFeedbackChange(episode.episode_number, e.target.value)}
                      placeholder="Enter your feedback..."
                      className="w-full p-3 bg-zinc-800 text-zinc-100 rounded-lg border border-zinc-700 focus:outline-none focus:border-zinc-600 resize-none min-h-[100px]"
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-[#2a2a2a]">
          <div className="flex justify-between items-center">
            <button
              onClick={() => setCurrentBatch(prev => Math.max(prev - 1, 0))}
              disabled={currentBatch === 0 || isValidating}
              className="px-4 py-2 bg-zinc-800 text-zinc-100 rounded-lg hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>
            <button
              onClick={handleRefinement}
              disabled={isValidating || (refinementType === 'human' && episodes.some(ep => !feedback[ep.episode_number]))}
              className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isValidating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  {currentBatch < totalBatches - 1 ? 'Next Batch' : 'Complete'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 