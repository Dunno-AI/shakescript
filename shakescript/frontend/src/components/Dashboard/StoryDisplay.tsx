import React, { useState } from 'react';
import { Episode } from '../../types/story';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface StoryDisplayProps {
  title?: string;
  episodes: Episode[];
  isGenerating: boolean;
}

export const StoryDisplay: React.FC<StoryDisplayProps> = ({ title, episodes, isGenerating }) => {
  const [currentEpisode, setCurrentEpisode] = useState(0);

  const nextEpisode = () => {
    setCurrentEpisode((prev) => (prev + 1) % episodes.length);
  };

  const previousEpisode = () => {
    setCurrentEpisode((prev) => (prev - 1 + episodes.length) % episodes.length);
  };

  return (
    <div className="p-8 space-y-8">
      {title && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h1 className="text-4xl font-bold text-zinc-100">
            {title}
          </h1>
          <div className="h-1 w-20 bg-emerald-500 rounded-full"></div>
        </motion.div>
      )}
      
      <div className="relative">
        {episodes.length > 0 && (
          <>
            <AnimatePresence mode="wait">
              <motion.div
                key={currentEpisode}
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.3 }}
                className="p-6 bg-zinc-900/30 rounded-xl border border-zinc-800 backdrop-blur-sm"
              >
                <h2 className="text-xl font-semibold mb-4 text-zinc-100">
                  Episode {episodes[currentEpisode].episode_number}: {episodes[currentEpisode].episode_title}
                </h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-zinc-400 leading-relaxed">
                    {episodes[currentEpisode].episode_content}
                  </p>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={previousEpisode}
                disabled={episodes.length <= 1}
                className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
              </button>
              
              {/* Pagination */}
              <div className="flex items-center gap-2">
                {episodes.map((_, index) => (
                  <button
                    key={`pagination-${index}`}
                    onClick={() => setCurrentEpisode(index)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      currentEpisode === index 
                        ? 'bg-emerald-500 w-4' 
                        : 'bg-zinc-700 hover:bg-zinc-600'
                    }`}
                  />
                ))}
              </div>

              <button
                onClick={nextEpisode}
                disabled={episodes.length <= 1}
                className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={20} />
              </button>
            </div>

            {/* Episode Counter */}
            <div className="mt-4 text-center text-sm text-zinc-500">
              Episode {currentEpisode + 1} of {episodes.length}
            </div>
          </>
        )}
      </div>
    </div>
  );
};