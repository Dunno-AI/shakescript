import React from 'react';
import { StoryDisplay } from './StoryDisplay';
import { Episode } from '../../types/story';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface StoryProps {
  story: {
    title?: string;
    episodes: Episode[];
  };
  isGenerating: boolean;
}

export const Story: React.FC<StoryProps> = ({ story, isGenerating }) => {
  return (
    <div className="flex-1 overflow-y-auto pb-32 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[#0A0A0A]">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0A0A] to-[#0A0A0A]"></div>
      </div>

      <div className="relative">
        {story.episodes.length === 0 && !isGenerating ? (
          <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center space-y-6 max-w-2xl mx-auto"
            >
              <div className="flex items-center justify-center">
                <Sparkles className="w-12 h-12 text-emerald-500" />
              </div>
              <h1 className="text-5xl font-bold text-zinc-100">
                Create Your Story
              </h1>
              <p className="text-xl text-zinc-400 max-w-lg mx-auto">
                Click the "New Thread" button to start generating your unique story with AI-powered storytelling.
              </p>
            </motion.div>
          </div>
        ) : (
          <div className="relative max-w-4xl mx-auto">
            {isGenerating ? (
              <div className="p-8 space-y-8">
                {/* Title Skeleton */}
                <div className="space-y-4">
                  <div className="h-12 bg-zinc-800/50 rounded-lg w-3/4 animate-pulse"></div>
                  <div className="h-6 bg-zinc-800/50 rounded-lg w-1/2 animate-pulse"></div>
                </div>

                {/* Episodes Skeleton */}
                <div className="space-y-6">
                  {[...Array(3)].map((_, index) => (
                    <div key={index} className="space-y-4 p-6 bg-zinc-900/30 rounded-xl border border-zinc-800">
                      <div className="h-8 bg-zinc-800/50 rounded-lg w-2/3 animate-pulse"></div>
                      <div className="space-y-3">
                        <div className="h-4 bg-zinc-800/50 rounded w-full animate-pulse"></div>
                        <div className="h-4 bg-zinc-800/50 rounded w-5/6 animate-pulse"></div>
                        <div className="h-4 bg-zinc-800/50 rounded w-4/5 animate-pulse"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <StoryDisplay
                title={story.title}
                episodes={story.episodes}
                isGenerating={isGenerating}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};