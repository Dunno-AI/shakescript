import { useEffect, useState } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Filter } from "lucide-react";
import StoryCard from "./StoryCard";
import ConfirmModal from "../../utils/ConfirmModal";
import { StoryDetails, StoryCache, Story } from "@/types/story";

interface LibraryListProps {
  onSelectStory: (story: StoryDetails) => void;
}

const CACHE_DURATION = 6 * 60 * 1000;
const ClassicLoader = () => {
  return (
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500" />
  );
};
const LibraryList = ({ onSelectStory }: LibraryListProps) => {
  const [stories, setStories] = useState<Story[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [cache, setCache] = useState<StoryCache | null>(null);
  const [genreFilter, setGenreFilter] = useState<string>('All');
  const [allGenres, setAllGenres] = useState<string[]>([]);
  const BASE_URL = import.meta.env.VITE_BACKEND_URL
  console.log(BASE_URL)

  useEffect(() => {
    if (cache && Date.now() - cache.timestamp < CACHE_DURATION) {
      setStories(cache.data);
      setLoading(false);
      // Set genres from cache
      const genres = Array.from(
        new Set(
          (cache.data.map((s: any) => typeof s.genre === 'string' ? s.genre : '') as string[])
            .filter((g: string): g is string => !!g)
        )
      );
      setAllGenres(['All', ...genres]);
    } else fetchStories();
  }, []);

  const fetchStories = async () => {
    try {
      const res = await axios.get(BASE_URL+"/api/v1/stories/all");
      // Only show completed stories in the library
      const completedStories = res.data.stories.filter((s: any) => s.is_completed);
      setStories(completedStories);
      setCache({ data: completedStories, timestamp: Date.now() });
      // Set genres
      const genres = Array.from(
        new Set(
          (completedStories.map((s: any) => typeof s.genre === 'string' ? s.genre : '') as string[])
            .filter((g: string): g is string => !!g)
        )
      );
      setAllGenres(['All', ...genres]);
    } catch (err) {
      console.error("Failed fetching stories", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id: number) => {
    setDeleteTarget(id);
    setShowConfirm(true);
  };

  const confirmDelete = async () => {
    try {
      if (deleteTarget !== null) {
        await axios.delete(
          `${BASE_URL}/api/v1/stories/${deleteTarget}`,
        );
        setStories(stories.filter((s) => s.story_id !== deleteTarget));
        setCache((prev) =>
          prev
            ? {
                ...prev,
                data: prev.data.filter((s) => s.story_id !== deleteTarget),
              }
            : null,
        );
      }
    } catch {
      alert("Failed to delete.");
    } finally {
      setShowConfirm(false);
      setDeleteTarget(null);
      setDeleting(false);
    }
  };

  // Filter by search and genre
  const filtered = stories.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
    (genreFilter === 'All' || s.genre === genreFilter)
  );

  return (
    <div className="max-w-5xl mx-auto">
      <ConfirmModal
        open={showConfirm}
        onConfirm={confirmDelete}
        onCancel={() => setShowConfirm(false)}
        message={
          deleting
            ? "Deleting..."
            : "Are you sure you want to delete this story? This action cannot be undone."
        }
      />

      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400 w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search stories..."
            className="w-full pl-10 pr-4 py-3 bg-[#111111] text-zinc-100 rounded-lg border border-zinc-800"
          />
        </div>
        <div className="relative" style={{ minWidth: 220 }}>
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400 w-5 h-5 pointer-events-none" />
          <select
            value={genreFilter}
            onChange={e => setGenreFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-[#111111] text-zinc-400 rounded-lg border border-zinc-800 focus:outline-none focus:border-zinc-600 text-base appearance-none"
            style={{ height: 48 }}
          >
            <option value="All" className="text-zinc-400 rounded-lg">All</option>
            {allGenres.filter(g => g !== 'All').map((genre) => (
              <option key={genre} value={genre} className="text-zinc-400 ">{genre}</option>
            ))}
          </select>
          <span className="pointer-events-none absolute right-4 top-1/2 transform -translate-y-1/2 text-zinc-400">▼</span>
        </div>
      </div>

      {!loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 place-items-center">
          <AnimatePresence>
            {filtered.map((story) => (
              <motion.div
                key={story.story_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <StoryCard
                  story={story}
                  onSelectStory={onSelectStory}
                  onDelete={() => handleDelete(story.story_id)}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center space-y-3">
          <ClassicLoader />
          <p className="text-xs text-zinc-500">Loading stories</p>
        </div>
      )}
    </div>
  );
};

export default LibraryList;

