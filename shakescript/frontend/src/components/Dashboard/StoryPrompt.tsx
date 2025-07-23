import React, { useState, useEffect, useRef } from 'react';
import { Send, ChevronUp, ChevronDown, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom'; // Add this import
import axios from 'axios';
import { useStoryContext } from '@/contexts/StoryListContext';
import { StoryDetails } from '@/types/story';

interface StoryPromptProps {
  onClose: () => void;
}

// Create a style element for the scrollbar styles
const ScrollbarStyles = () => {
  return (
    <style>
      {`
        textarea::-webkit-scrollbar {
          width: 6px;
        }
        textarea::-webkit-scrollbar-track {
          background: #18181b;
        }
        textarea::-webkit-scrollbar-thumb {
          background-color: #3f3f46;
          border-radius: 10px;
          border: 2px solid #18181b;
        }
        textarea {
          scrollbar-width: thin;
          scrollbar-color: #3f3f46 #18181b;
          -ms-overflow-style: none;
        }
      `}
    </style>
  );
};

export const StoryPrompt: React.FC<StoryPromptProps> = ({ onClose }) => {
  const [prompt, setPrompt] = useState("");
  const [episodes, setEpisodes] = useState(5);
  const [refineMethod, setRefineMethod] = useState<'human' | 'ai'>('human');
  const [isCreatingStory, setIsCreatingStory] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const navigate = useNavigate(); 
  const BASE_URL = import.meta.env.VITE_BACKEND_URL
  const { addStory } = useStoryContext()

  // Auto-resize textarea when content changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [prompt]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || episodes <= 0 || isCreatingStory) return;
    
    setIsCreatingStory(true);

    try {
      const storyResponse = await axios.post(`${BASE_URL}/api/v1/stories/`, {
        prompt,
        num_episodes: episodes,
        batch_size: 1, // Always 1
        refinement: refineMethod === "ai" ? "AI": "HUMAN",
      });
      
      if (storyResponse.data.story && storyResponse.data.story.story_id) {
        const newStoryId = storyResponse.data.story.story_id;
        addStory(storyResponse.data.story);
        const story : StoryDetails = {
          story_id: newStoryId,
          batch_size: 1,
          refinement_method: refineMethod === "ai" ? "AI": "HUMAN",
          total_episodes: episodes,
          current_episode: 1,
          summary: "",
          title: storyResponse.data.story.title,
          episodes: [],
        }

        navigate(`/dashboard/${newStoryId}/refinement`, {
          state: {
            story: story, 
            isHinglish: false,
            initialBatch: 1,
          }
        });
        
        onClose(); 
      } else {
        console.error('No story ID found in response');
        alert('Failed to get story ID. Please try again.');
      }
    } catch (error) {
      console.error('Error creating story:', error);
      alert('Failed to create story. Please try again.');
    } finally {
      setIsCreatingStory(false);
    }
  };

  const incrementEpisodes = () => {
    setEpisodes((prev) => Math.min(prev + 1, 50));
  };

  const decrementEpisodes = () => {
    setEpisodes((prev) => Math.max(prev - 1, 1));
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-10 bg-black bg-opacity-50">
      <ScrollbarStyles />
     
      <div className="bg-[#111111] rounded-xl border border-[#2a2a2a] shadow-lg w-full max-w-3xl mx-3">
        <div className="p-7">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-zinc-100">Create Your Story</h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-zinc-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-zinc-400" />
            </button>
          </div>
         
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="block text-zinc-400 text-sm mb-2">
                Enter the prompt for your story:
              </label>
              <div className="relative">
                <textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your story idea..."
                  className="w-full p-4 bg-zinc-900 text-zinc-100 rounded-lg border border-zinc-800 focus:outline-none focus:border-zinc-700 resize-none min-h-[120px] max-h-[200px] overflow-y-auto"
                  disabled={isCreatingStory}
                  rows={3}
                />
              </div>
            </div>
            <div className="flex flex-row items-end justify-between gap-4">
              <div className="flex flex-col gap-2 w-full max-w-xs">
                <div className="flex items-center">
                  <label className="text-zinc-400 text-sm w-32">Episodes:</label>
                  <div className="relative flex items-center">
                    <input
                      type="number"
                      value={episodes}
                      onChange={(e) => setEpisodes(Number.parseInt(e.target.value) || 1)}
                      min="1"
                      max="50"
                      className="w-36 h-8 px-2 py-1 bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 text-sm appearance-none"
                      disabled={isCreatingStory}
                    />
                    <div className="absolute right-0 top-0 bottom-0 flex flex-col">
                      <button
                        type="button"
                        onClick={incrementEpisodes}
                        className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-zinc-700 rounded-tr-md hover:bg-zinc-700"
                        disabled={isCreatingStory || episodes >= 50}
                      >
                        <ChevronUp size={12} className="text-zinc-400" />
                      </button>
                      <button
                        type="button"
                        onClick={decrementEpisodes}
                        className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-t border-zinc-700 rounded-br-md hover:bg-zinc-700"
                        disabled={isCreatingStory || episodes <= 1}
                      >
                        <ChevronDown size={12} className="text-zinc-400" />
                      </button>
                    </div>
                  </div>
                </div>
                <div className="flex items-center">
                  <label className="text-zinc-400 text-sm w-32">Refinement:</label>
                  <div className="relative w-36">
                    <select
                      id="refine-method"
                      value={refineMethod}
                      onChange={(e) => setRefineMethod(e.target.value as 'human' | 'ai')}
                      className="w-36 h-8 px-2 py-1 bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 text-sm"
                      disabled={isCreatingStory}
                    >
                      <option value="ai" disabled title="Upgrade to Premium to unlock">AI</option>
                      <option value="human">Human</option>
                    </select>
                    {/* Tooltip for AI option */}
                    <div
                      className="pointer-events-none absolute left-0 top-0 w-full h-full flex items-center"
                      style={{ zIndex: 10 }}
                    >
                      {refineMethod === 'ai' && (
                        <div className="absolute left-0 top-10 w-44 bg-zinc-900 text-zinc-100 text-xs rounded shadow-lg px-3 py-2 border border-zinc-700" style={{display: 'block'}}>
                          Upgrade to Premium to unlock
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end w-full max-w-[140px]">
                {isCreatingStory ? (
                  <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500"></div>
                ) : (
                  <button
                    type="submit"
                    disabled={!prompt.trim()}
                    className="px-3 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 w-full min-w-[120px]"
                  >
                    <Send className="w-4 h-4" />
                    <span className="text-sm font-medium">Generate</span>
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
