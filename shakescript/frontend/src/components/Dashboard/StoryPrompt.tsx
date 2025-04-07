import React, { useState, useEffect, useRef } from 'react';
import { Send, ChevronUp, ChevronDown, X } from 'lucide-react';

interface StoryPromptProps {
  onSubmit: (prompt: string, episodes: number, isHinglish: boolean) => void;
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
      onSubmit(prompt, episodes, isHinglish);
    }
  };

  const incrementEpisodes = () => {
    setEpisodes((prev) => Math.min(prev + 1, 50));
  };

  const decrementEpisodes = () => {
    setEpisodes((prev) => Math.max(prev - 1, 1));
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
           
            <div className="flex items-center mb-8">
              {/* Hinglish Checkbox on left */}
              <div className="flex items-center">
                <div className="relative inline-block w-10 mr-2 align-middle">
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
                <label htmlFor="hinglish-toggle" className="text-zinc-400 text-sm cursor-pointer">Hinglish</label>
              </div>

              {/* Episodes Counter - pushed all the way to right */}
              <div className="flex items-center ml-auto">
                <span className="text-zinc-400 text-sm mr-2">Episodes:</span>
                <div className="relative flex items-center">
                  <input
                    type="number"
                    value={episodes}
                    onChange={(e) => setEpisodes(Number.parseInt(e.target.value) || 1)}
                    min="1"
                    max="50"
                    className="w-16 h-8 px-2 py-1 bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 focus:outline-none focus:border-zinc-600 text-sm appearance-none"
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