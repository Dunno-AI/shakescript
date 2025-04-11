import React, { useState, useEffect, useRef } from 'react';
import { Send, ChevronUp, ChevronDown, X } from 'lucide-react';

interface StoryPromptProps {
  onSubmit: (prompt: string, episodes: number, isHinglish: boolean, refineMethod: 'human' | 'ai', batchSize: number) => void;
  isGenerating: boolean;
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

export const StoryPrompt: React.FC<StoryPromptProps> = ({ onSubmit, isGenerating, onClose }) => {
  const [prompt, setPrompt] = useState("");
  const [episodes, setEpisodes] = useState(5);
  const [isHinglish, setIsHinglish] = useState(false);
  const [refineMethod, setRefineMethod] = useState<'human' | 'ai'>('ai');
  const [batchSize, setBatchSize] = useState(2);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea when content changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [prompt]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && episodes > 0) {
      onSubmit(prompt, episodes, isHinglish, refineMethod, batchSize);
    }
  };

  const incrementEpisodes = () => {
    setEpisodes((prev) => Math.min(prev + 1, 50));
  };

  const decrementEpisodes = () => {
    setEpisodes((prev) => Math.max(prev - 1, 1));
  };

  const incrementBatchSize = () => {
    setBatchSize((prev) => Math.min(prev + 1, episodes));
  };

  const decrementBatchSize = () => {
    setBatchSize((prev) => Math.max(prev - 1, 1));
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-10 bg-black bg-opacity-10">
      {/* Include the scrollbar styles */}
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
                What kind of story do you want?
              </label>
              <div className="relative">
                <textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your story idea..."
                  className="w-full p-4 bg-zinc-900 text-zinc-100 rounded-lg border border-zinc-800 focus:outline-none focus:border-zinc-700 resize-none min-h-[120px] max-h-[200px] overflow-y-auto"
                  disabled={isGenerating}
                  rows={3}
                />
              </div>
            </div>
           
            <div className="space-y-4 mb-8">
              {/* Episodes Counter */}
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
                    disabled={isGenerating}
                  />
                  <div className="absolute right-0 top-0 bottom-0 flex flex-col">
                    <button
                      type="button"
                      onClick={incrementEpisodes}
                      className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-zinc-700 rounded-tr-md hover:bg-zinc-700"
                      disabled={isGenerating || episodes >= 50}
                    >
                      <ChevronUp size={12} className="text-zinc-400" />
                    </button>
                    <button
                      type="button"
                      onClick={decrementEpisodes}
                      className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-t border-zinc-700 rounded-br-md hover:bg-zinc-700"
                      disabled={isGenerating || episodes <= 1}
                    >
                      <ChevronDown size={12} className="text-zinc-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Batch Size Counter */}
              <div className="flex items-center">
                <label className="text-zinc-400 text-sm w-32">Batch Size:</label>
                <div className="relative flex items-center">
                  <input
                    type="number"
                    value={batchSize}
                    onChange={(e) => setBatchSize(Number.parseInt(e.target.value) || 1)}
                    min="1"
                    max={episodes}
                    className="w-36 h-8 px-2 py-1 bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 text-sm appearance-none"
                    disabled={isGenerating}
                  />
                  <div className="absolute right-0 top-0 bottom-0 flex flex-col">
                    <button
                      type="button"
                      onClick={incrementBatchSize}
                      className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-zinc-700 rounded-tr-md hover:bg-zinc-700"
                      disabled={isGenerating || batchSize >= episodes}
                    >
                      <ChevronUp size={12} className="text-zinc-400" />
                    </button>
                    <button
                      type="button"
                      onClick={decrementBatchSize}
                      className="flex-1 flex items-center justify-center px-1 bg-zinc-800 border-l border-t border-zinc-700 rounded-br-md hover:bg-zinc-700"
                      disabled={isGenerating || batchSize <= 1}
                    >
                      <ChevronDown size={12} className="text-zinc-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Refinement Method Dropdown */}
              <div className="flex items-center">
                <label className="text-zinc-400 text-sm w-32">Refinement:</label>
                <select
                  id="refine-method"
                  value={refineMethod}
                  onChange={(e) => setRefineMethod(e.target.value as 'human' | 'ai')}
                  className="w-36 h-8 px-2 py-1 bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 text-sm"
                  disabled={isGenerating}
                >
                  <option value="ai">AI</option>
                  <option value="human">Human</option>
                </select>
              </div>

              {/* Divider line */}
              <div className="border-t border-zinc-800"></div>

              {/* Hinglish Toggle - Moved to right */}
              <div className="flex items-center justify-end">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-zinc-400 text-sm">English</span>
                    <div className="relative inline-block w-10 align-middle">
                      <input
                        type="checkbox"
                        checked={isHinglish}
                        onChange={(e) => setIsHinglish(e.target.checked)}
                        className="sr-only"
                        id="hinglish-toggle"
                        disabled={isGenerating}
                      />
                      <label
                        htmlFor="hinglish-toggle"
                        className="block overflow-hidden h-5 rounded-full bg-zinc-800 cursor-pointer"
                      >
                        <span
                          className={`block h-4 w-4 ml-0.5 mt-0.5 rounded-full bg-zinc-400 transform transition-transform duration-200 ease-in ${
                            isHinglish ? 'translate-x-5 bg-zinc-300' : ''
                          }`}
                        ></span>
                      </label>
                    </div>
                    <span className="text-zinc-400 text-sm">Hinglish</span>
                  </div>
                </div>
              </div>
            </div>
           
            <div className="flex justify-end gap-3">
              {isGenerating ? (
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500"></div>
              ) : (
                <button
                  type="submit"
                  disabled={!prompt.trim()}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Generate Story</span>
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};