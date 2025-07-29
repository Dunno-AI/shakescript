import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Filter, Loader2 } from "lucide-react";
import StoryCard from "./StoryCard";
import ConfirmModal from "../../utils/ConfirmModal";
import { useStoryContext } from "@/contexts/StoryListContext";
import { Story, StoryDetails } from "@/types/story";
import { SpinLoading } from "respinner";

interface LibraryListProps {
  onSelectStory: (story: StoryDetails) => void;
  Stories: Story[];
}

const LibraryList = ({ onSelectStory, Stories }: LibraryListProps) => {
  const { deleteStory, loading } = useStoryContext();

  const [searchQuery, setSearchQuery] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [genreFilter, setGenreFilter] = useState<string>("All");
  const [allGenres, setAllGenres] = useState<string[]>([]);

  useEffect(() => {
    const genres = Array.from(
      new Set(
        Stories.map((s) => (typeof s.genre === "string" ? s.genre : "")).filter(
          (g): g is string => !!g,
        ),
      ),
    );
    setAllGenres(["All", ...genres]);
  }, [Stories]);

  const handleDelete = (id: number) => {
    setDeleteTarget(id);
    setShowConfirm(true);
  };

  const confirmDelete = async () => {
    if (deleteTarget !== null) {
      setDeleting(true);
      try {
        await deleteStory(deleteTarget);
      } catch (err) {
      } finally {
        setShowConfirm(false);
        setDeleteTarget(null);
        setDeleting(false);
      }
    }
  };

  const filtered = Stories.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (genreFilter === "All" || s.genre === genreFilter),
  );

  return (
    <div className="max-w-5xl mx-auto">
      <ConfirmModal
        open={showConfirm}
        onConfirm={confirmDelete}
        onCancel={() => setShowConfirm(false)}
        message="Are you sure you want to delete this story? This action cannot be undone."
        isDeleting={deleting}
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
            onChange={(e) => setGenreFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-[#111111] text-zinc-400 rounded-lg border border-zinc-800 focus:outline-none focus:border-zinc-600 text-base appearance-none"
            style={{ height: 48 }}
          >
            <option value="All" className="text-zinc-400 rounded-lg">
              All
            </option>
            {allGenres
              .filter((g) => g !== "All")
              .map((genre) => (
                <option key={genre} value={genre} className="text-zinc-400">
                  {genre}
                </option>
              ))}
          </select>
          <span className="pointer-events-none absolute right-4 top-1/2 transform -translate-y-1/2 text-zinc-400">
            ▼
          </span>
        </div>
      </div>

      {!loading ? (filtered.length > 0 ? (
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
        <div className="text-center py-20 bg-zinc-900/50 rounded-lg border border-dashed border-zinc-700">
          <h2 className="text-xl font-semibold text-zinc-300">No Stories</h2>
          <p className="text-zinc-500 mt-2">Create some stories to see the list here.</p>
        </div>
      )) : (
        <div className="flex flex-col items-center justify-center space-y-3">
          <SpinLoading fill="#777" borderRadius={4} count={12} />
          <p className="text-xs text-zinc-500">Loading stories</p>
        </div>
      )}
    </div>
  );
};

export default LibraryList;
