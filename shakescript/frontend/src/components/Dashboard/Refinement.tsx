import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Check, PenLine, Loader2, ArrowRight } from 'lucide-react';

interface RefinementProps {
  storyId: number;
  totalEpisodes: number;
  batchSize: number;
  refinementType: 'human' | 'ai';
  isHinglish: boolean;
  onComplete: () => void;
  onClose: () => void;
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
  onClose
}) => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [status, setStatus] = useState<'loading' | 'refining' | 'ready' | 'complete'>('loading');
  const [currentBatch, setCurrentBatch] = useState<number>(1);
  const [feedback, setFeedback] = useState<{ [key: number]: string }>({});
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

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
    console.log("Generating batch for storyId:", storyId);
    setStatus('loading');
    setErrorMessage('');
    
    try {
      console.log('With params:', {
        batch_size: batchSize,
        hinglish: isHinglish,
        refinement_type: refinementType
      });
      
      const response = await axios.post(
        `http://localhost:8000/api/v1/episodes/${storyId}/generate-batch`,
        {},
        {
          params: {
            batch_size: batchSize,
            hinglish: isHinglish,
            refinement_type: refinementType
          }
        }
      );

      console.log('Generate batch response:', response.data);

      if (response.data.status === 'success') {
        // Map API response to only include episode_content as content
        const mappedEpisodes = response.data.episodes.map((ep: any) => ({
          episode_number: ep.episode_number,
          content: ep.episode_content,
        }));
        setEpisodes(mappedEpisodes);
        // If AI refinement, move directly to ready state
        // If human refinement, prepare for human input
        setStatus(refinementType === 'ai' ? 'ready' : 'refining');
        // Initialize feedback object
        const initialFeedback: { [key: number]: string } = {};
        mappedEpisodes.forEach((ep: any) => {
          initialFeedback[ep.episode_number] = '';
        });
        setFeedback(initialFeedback);
      } else {
        if (response.data.message && response.data.message.includes("All episodes generated")) {
          console.log('Story generation complete');
          setStatus('complete');
          onComplete();
        } else {
          console.log('Error in response:', response.data.message);
          setErrorMessage(response.data.message || 'Failed to generate episodes');
        }
      }
    } catch (error: any) {
      console.error('Error generating batch:', error);
      setErrorMessage(
        `Failed to connect to the server: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`
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
    console.log('Submitting feedback for storyId:', storyId);
    setIsSubmitting(true);
    
    try {
      // Only submit feedback for episodes that have feedback text
      const feedbackToSubmit: Feedback[] = Object.entries(feedback)
        .filter(([_, text]) => text.trim().length > 0)
        .map(([episodeNumber, text]) => ({
          episode_number: parseInt(episodeNumber),
          feedback: text
        }));

      console.log('Feedback to submit:', feedbackToSubmit);

      if (feedbackToSubmit.length > 0) {
        console.log(`Calling API: POST http://localhost:8000/api/v1/episodes/${storyId}/refine-batch`);
        const response = await axios.post(
          `http://localhost:8000/api/v1/episodes/${storyId}/refine-batch`,
          feedbackToSubmit
        );

        console.log('Refine batch response:', response.data);

        if (response.data.status === 'pending' || response.data.episodes) {
          console.log('Refined episodes received:', response.data.episodes.length);
          setEpisodes(response.data.episodes);
          
          // Reset feedback after refinement
          const newFeedback: { [key: number]: string } = {};
          response.data.episodes.forEach((ep: Episode) => {
            newFeedback[ep.episode_number] = '';
          });
          setFeedback(newFeedback);
        }
      } else {
        console.log('No feedback to submit, moving directly to ready state');
      }
      
      // Move to ready state after feedback processing
      setStatus('ready');
    } catch (error: any) {
      console.error('Error submitting feedback:', error);
      setErrorMessage(
        `Failed to submit feedback: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const validateBatch = async () => {
    console.log('Validating batch for storyId:', storyId);
    setIsSubmitting(true);
    
    try {
      console.log(`Calling API: POST http://localhost:8000/api/v1/episodes/${storyId}/validate-batch`);
      const response = await axios.post(
        `http://localhost:8000/api/v1/episodes/${storyId}/validate-batch`
      );

      console.log('Validate batch response:', response.data);

      if (response.data.status === 'success') {
        if (response.data.message && response.data.message.includes('Story complete')) {
          console.log('Story generation complete');
          setStatus('complete');
          onComplete();
        } else {
          console.log('Moving to next batch');
          // Increment batch counter and generate the next batch
          setCurrentBatch(prev => prev + 1);
          setTimeout(() => {
            generateBatch();
          }, 500); // Small delay to ensure UI updates properly
        }
      } else {
        console.log('Error in validation response:', response.data);
        setErrorMessage(response.data.message || 'Failed to validate episodes');
      }
    } catch (error: any) {
      console.error('Error validating batch:', error);
      setErrorMessage(
        `Failed to validate batch: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please try again.`
      );
    } finally {
      setIsSubmitting(false);
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
              <Loader2 className="w-8 h-8 text-emerald-500 animate-spin mb-4" />
              <p className="text-zinc-300">Generating episodes...</p>
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
            <div className="space-y-6">
              {episodes.map((episode) => (
                <div key={episode.episode_number} className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
                  <div className="text-zinc-300 whitespace-pre-wrap mb-4">{episode.content}</div>
                  {status === 'refining' && refinementType === 'human' && (
                    <div>
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
