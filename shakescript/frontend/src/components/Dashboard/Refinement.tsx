import React, { useState, useEffect, useRef } from 'react';
import { useAuthFetch } from '../../lib/utils';
import { X, Check, PenLine, Loader2, ArrowRight } from 'lucide-react';
import { TypingAnimation } from '../utils/TypingAnimation';

interface RefinementProps {
  storyId: number;
  totalEpisodes: number;
  batchSize: number;
  refinementType: 'human' | 'ai';
  isHinglish: boolean;
  onComplete: () => void;
  onClose: () => void;
  initialBatch?: number;
}

interface Episode {
  episode_number: number;
  title: string;
  content: string;
  feedback?: string;
}

interface Feedback {
  episode_number: number;
  feedback: string;
}

export const Refinement: React.FC<RefinementProps> = ({
  storyId,
  totalEpisodes,
  batchSize,
  refinementType,
  isHinglish,
  onComplete,
  onClose,
  initialBatch
}) => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [status, setStatus] = useState<'loading' | 'refining' | 'ready' | 'complete'>('loading');
  const [currentBatch, setCurrentBatch] = useState<number>(initialBatch || 1);
  const [feedback, setFeedback] = useState<{ [key: number]: string }>({});
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const BASE_URL = import.meta.env.VITE_BACKEND_URL
  const authFetch = useAuthFetch();

  // Calculate progress
  const progress = Math.min(
    ((currentBatch - 1) * batchSize + episodes.length) / totalEpisodes * 100,
    100
  );
  
  // Generate initial batch on component mount
  useEffect(() => {
    console.log("Refinement component mounted with storyId:", storyId);
    if (storyId) {
      generateBatch();
    }
  }, [storyId]);

  const generateBatch = async () => {
    setStatus('loading');
    setErrorMessage('');
    try {
      const params = new URLSearchParams({
        batch_size: batchSize.toString(),
        hinglish: isHinglish.toString(),
        refinement_type: refinementType
      });
      const response = await authFetch(
        `${BASE_URL}/api/v1/episodes/${storyId}/generate-batch?${params.toString()}`,
        {
          method: 'POST',
        }
      );
      const data = await response.json();
      if (data.status === 'success') {
        const mappedEpisodes = data.episodes.map((ep: any) => ({
          episode_number: ep.episode_number,
          content: ep.episode_content,
        }));
        setEpisodes(mappedEpisodes);
        setStatus(refinementType === 'ai' ? 'ready' : 'refining');
        const initialFeedback: { [key: number]: string } = {};
        mappedEpisodes.forEach((ep: any) => {
          initialFeedback[ep.episode_number] = '';
        });
        setFeedback(initialFeedback);
      } else {
        if (data.message && data.message.includes("All episodes generated")) {
          setStatus('complete');
          onComplete();
        } else {
          setErrorMessage(data.message || 'Failed to generate episodes');
        }
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to connect to the server: ${error.message || 'Unknown error'}. Please try again.`
      );
    }
  };

  const handleFeedbackChange = (episodeNumber: number, value: string) => {
    setFeedback(prev => ({
      ...prev,
      [episodeNumber]: value
    }));
  };

  const submitFeedback = async () => {
    setIsSubmitting(true);
    try {
      const feedbackToSubmit: Feedback[] = Object.entries(feedback)
        .filter(([_, text]) => text.trim().length > 0)
        .map(([episodeNumber, text]) => ({
          episode_number: parseInt(episodeNumber),
          feedback: text
        }));
      if (feedbackToSubmit.length > 0) {
        const response = await authFetch(
          `${BASE_URL}/api/v1/episodes/${storyId}/refine-batch`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackToSubmit),
          }
        );
        const data = await response.json();
        if (data.status === 'pending' || data.episodes) {
          setEpisodes(data.episodes);
          const newFeedback: { [key: number]: string } = {};
          data.episodes.forEach((ep: Episode) => {
            newFeedback[ep.episode_number] = '';
          });
          setFeedback(newFeedback);
        }
      }
      setStatus('ready');
    } catch (error: any) {
      setErrorMessage(
        `Failed to submit feedback: ${error.message || 'Unknown error'}. Please try again.`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const validateBatch = async () => {
    setIsSubmitting(true);
    try {
      const response = await authFetch(
        `${BASE_URL}/api/v1/episodes/${storyId}/validate-batch`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.status === 'success') {
        if (data.message && data.message.includes('Story complete')) {
          await authFetch(`${BASE_URL}/api/v1/stories/${storyId}/complete`, { method: 'POST' });
          setStatus('complete');
          onComplete();
        } else {
          setCurrentBatch(prev => prev + 1);
          setTimeout(() => {
            generateBatch();
          }, 500);
        }
      } else {
        setErrorMessage(data.message || 'Failed to validate episodes');
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to validate batch: ${error.message || 'Unknown error'}. Please try again.`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const episodesEndRef = useRef<HTMLDivElement | null>(null);
  const scrollToBottom = () => {
    if (episodesEndRef.current) {
      episodesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-20 bg-black bg-opacity-50">
      
      <div className="bg-[#111111] rounded-xl border border-[#2a2a2a] shadow-lg w-full max-w-4xl mx-3 max-h-[90vh] flex flex-col">
        <div className="p-5 border-b border-zinc-800 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-zinc-100">
            {status === 'complete' 
              ? 'Story Generation Complete!' 
              : `Generating Episodes (Batch ${currentBatch})`}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-zinc-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-zinc-400" />
          </button>
        </div>
        
        {/* Progress bar */}
        <div className="px-5 py-3 border-b border-zinc-800">
          <div className="w-full bg-zinc-800 rounded-full h-2.5">
            <div 
              className="bg-emerald-500 h-2.5 rounded-full" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-zinc-400 mt-1">
            <span>{Math.min((currentBatch - 1) * batchSize + episodes.length, totalEpisodes)} of {totalEpisodes} episodes</span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>
        
        <div className="overflow-y-auto flex-1 p-5">
          {status === 'loading' && (
            <div className="flex flex-col items-center justify-center h-64">
              {/* <Loader2 className="w-8 h-8 text-emerald-500 animate-spin mb-4" /> */}
              <TypingAnimation text="Generating episodes..." speed={30} className="text-zinc-300 text-lg mb-4" />
            </div>
          )}
          
          {status === 'complete' && (
            <div className="flex flex-col items-center justify-center h-64">
              <Check className="w-12 h-12 text-emerald-500 mb-4" />
              <p className="text-xl font-medium text-zinc-200 mb-2">All episodes generated successfully!</p>
              <p className="text-zinc-400">You can now read your complete story.</p>
            </div>
          )}
          
          {(status === 'refining' || status === 'ready') && episodes.length > 0 && (
            <div className="space-y-6" style={{ position: 'relative' }}>
              {episodes.map((episode) => (
                <div key={episode.episode_number} className="bg-zinc-900 rounded-lg p-4 border border-zinc-800 pb-10">
                  <TypingAnimation
                    text={episode.content}
                    speed={15}
                    className="text-zinc-300 whitespace-pre-wrap mb-4"
                    onTyping={scrollToBottom}
                  />
                  {status === 'refining' && refinementType === 'human' && (
                    <div className='mt-4'>
                      <div className="flex items-center mb-2">
                        <PenLine className="w-4 h-4 text-zinc-400 mr-2" />
                        <label className="text-sm text-zinc-400">Feedback (optional)</label>
                      </div>
                      <textarea
                        value={feedback[episode.episode_number] || ''}
                        onChange={(e) => handleFeedbackChange(episode.episode_number, e.target.value)}
                        placeholder="Add your feedback for this episode..."
                        className="w-full p-3 bg-zinc-800 text-zinc-200 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 resize-y min-h-[80px]"
                      />
                    </div>
                  )}
                </div>
              ))}
              <div ref={episodesEndRef} />
            </div>
          )}
          
          {errorMessage && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-md text-red-200">
              {errorMessage}
            </div>
          )}
        </div>
        
        <div className="p-5 border-t border-zinc-800 flex justify-end gap-3">
          {status === 'refining' && (
            <>
              <button
                onClick={validateBatch}
                disabled={isSubmitting}
                className="px-4 py-2 bg-zinc-600 text-white rounded-lg hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                <span>Validate Batch</span>
              </button>
              <button
                onClick={submitFeedback}
                disabled={isSubmitting}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <PenLine className="w-4 h-4" />}
                <span>Submit Feedback</span>
              </button>
            </>
          )}
          
          {status === 'ready' && (
            <button
              onClick={validateBatch}
              disabled={isSubmitting}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              <span>Continue</span>
            </button>
          )}
          
        </div>
      </div>
    </div>
  );
};

