import { ChevronLeft, ChevronRight, ArrowLeft, Download } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { generatePDF } from "../utils/PDFGenerator";
import { X } from "lucide-react";
import { StoryCache } from "@/types/story";
import axios from "axios";
import ConfirmModal from "../utils/ConfirmModal";

interface Episode {
  id: number;
  number: number;
  title: string;
  content: string;
  summary?: string;
}

interface Story {
  story_id: number;
  title: string;
  summary: string;
  episodes: Episode[];
}

interface StoryReaderProps {
  story: Story;
  onBack: () => void;
}

const StoryReader = ({ story, onBack }: StoryReaderProps) => {
  const [currentEpisode, setCurrentEpisode] = useState(0);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [cache, setCache] = useState<StoryCache | null>(null);
  const BASE_URL = import.meta.env.VITE_BACKEND_URL

  const handleDelete = (id: number) => {
    setDeleteTarget(id);
    setShowConfirm(true);
  };
  const confirmDelete = async () => {
    try {
      if (deleteTarget !== null) {
        await axios.delete(`${BASE_URL}api/v1/stories/${deleteTarget}`);
        setCache(prev => prev ? { ...prev, data: prev.data.filter(s => s.story_id !== deleteTarget) } : null);
      }
      onBack();
    } catch {
      alert('Failed to delete.');
    } finally {
      setShowConfirm(false);
      setDeleteTarget(null);
      setDeleting(false);
    }
  };

  const nextEpisode = () =>
    setCurrentEpisode((prev) => (prev + 1) % story.episodes.length);
  const previousEpisode = () =>
    setCurrentEpisode(
      (prev) => (prev - 1 + story.episodes.length) % story.episodes.length,
    );

  return (
    <div className="max-w-4xl mx-auto">
      <ConfirmModal
        open={showConfirm}
        onConfirm={confirmDelete}
        onCancel={() => setShowConfirm(false)}
        message={deleting ? 'Deleting...' : 'Are you sure you want to delete this story? This action cannot be undone.'}
      />
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
            onClick={()=>generatePDF(story)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
          >
            <Download size={20} />
            <span>Download PDF</span>
          </button>
          <button
            onClick={() => handleDelete(story.story_id)}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <X size={20} />
            <span>Delete</span>
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
                Episode {story.episodes[currentEpisode].number}:{" "}
                {story.episodes[currentEpisode].title}
              </h2>
              <div className="prose prose-invert max-w-none">
                <p className="text-zinc-400 leading-relaxed">
                  {story.episodes[currentEpisode].content}
                </p>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={previousEpisode}
              disabled={story.episodes.length <= 1}
              className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={20} />
            </button>

            {/* Pagination */}
            <div className="flex items-center gap-2">
              {story.episodes.map((_, index) => (
                <button
                  key={`pagination-${index}`}
                  onClick={() => setCurrentEpisode(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    currentEpisode === index
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

          {/* Episode Counter */}
          <div className="mt-4 text-center text-sm text-zinc-500">
            Episode {currentEpisode + 1} of {story.episodes.length}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryReader;
