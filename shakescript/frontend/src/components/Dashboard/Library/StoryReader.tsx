import { ChevronLeft, ChevronRight, ArrowLeft, Download } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { generatePDF } from "../../utils/PDFGenerator";
import { StoryDetails } from "@/types/story";

interface StoryReaderProps {
  story: StoryDetails;
  onBack: () => void;
}

const StoryReader = ({ story, onBack }: StoryReaderProps) => {
  const [currentEpisode, setCurrentEpisode] = useState(0);

  const nextEpisode = () => {
    if (story.episodes.length > 0) {
      setCurrentEpisode((prev) => (prev + 1) % story.episodes.length);
    }
  };

  const previousEpisode = () => {
    if (story.episodes.length > 0) {
      setCurrentEpisode(
        (prev) => (prev - 1 + story.episodes.length) % story.episodes.length,
      );
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>Back to Library</span>
        </button>
        <div className="flex gap-2">
          <button
            onClick={() => generatePDF(story)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
          >
            <Download size={20} />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-zinc-100 mb-4">
            {story.title}
          </h1>
          <p className="text-zinc-400">{story.summary}</p>
        </div>

        {story.episodes && story.episodes.length > 0 ? (
          <div className="relative">
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
                  Episode {story.episodes[currentEpisode].episode_number}:{" "}
                  {story.episodes[currentEpisode].episode_title}
                </h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-zinc-400 leading-relaxed">
                    {story.episodes[currentEpisode].episode_content}
                  </p>
                </div>
              </motion.div>
            </AnimatePresence>

            <div className="flex items-center justify-between mt-6">
              <button
                onClick={previousEpisode}
                disabled={story.episodes.length <= 1}
                className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
              </button>

              <div className="flex items-center gap-2">
                {story.episodes.map((_, index) => (
                  <button
                    key={`pagination-${index}`}
                    onClick={() => setCurrentEpisode(index)}
                    className={`w-2 h-2 rounded-full transition-all ${currentEpisode === index
                        ? "bg-emerald-500 w-4"
                        : "bg-zinc-700 hover:bg-zinc-600"
                      }`}
                  />
                ))}
              </div>

              <button
                onClick={nextEpisode}
                disabled={story.episodes.length <= 1}
                className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={20} />
              </button>
            </div>

            <div className="mt-4 text-center text-sm text-zinc-500">
              Episode {currentEpisode + 1} of {story.episodes.length}
            </div>
          </div>
        ) : (
          <div className="text-center text-zinc-500 p-8 bg-zinc-900/30 rounded-xl border border-zinc-800">
            This story has no episodes yet.
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryReader;
