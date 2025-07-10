import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Search, Download, ArrowLeft, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { cn } from "../../lib/utils";

interface Story {
  story_id: number;
  title: string;
}

interface Character {
  Name: string;
  Role: string;
  Description: string;
  Relationship: Record<string, any>;
  role_active: boolean;
}

interface StoryDetails {
  story_id: number;
  title: string;
  setting: string[];
  characters: Record<string, Character>;
  special_instructions: string;
  story_outline: Record<string, string>;
  current_episode: number;
  episodes: {
    id: number;
    number: number;
    title: string;
    content: string;
    summary: string;
  }[];
  summary: string;
}

// Add cache interfaces
interface StoryCache {
  data: Story[];
  timestamp: number;
}

interface StoryDetailsCache {
  [key: number]: {
    data: StoryDetails;
    timestamp: number;
  };
}

// Cache configuration
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

const ClassicLoader = () => {
  return (
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500" />
  );
};

// Confirmation Modal
const ConfirmModal = ({ open, onConfirm, onCancel, message }: { open: boolean; onConfirm: () => void; onCancel: () => void; message: string }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70">
      <div className="backdrop-blur-lg bg-zinc-950/95 p-10 rounded-2xl shadow-2xl border border-zinc-800 w-full max-w-lg mx-4">
        <div className="mb-6 text-zinc-100 text-xl text-center font-semibold">{message}</div>
        <div className="flex justify-center gap-8 mt-4">
          <button
            onClick={onCancel}
            className="px-6 py-3 rounded-lg bg-zinc-700 text-zinc-200 hover:bg-zinc-600 transition text-base font-medium"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-3 rounded-lg bg-red-600 text-white hover:bg-red-700 transition text-base font-medium shadow-md"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

const StoryCard = ({ 
  story, 
  onClick, 
  isLoading, 
  onDelete
}: { 
  story: Story; 
  onClick: () => void;
  isLoading: boolean;
  onDelete: (storyId: number) => void;
}) => {
  const common = "absolute flex w-full h-full [backface-visibility:hidden]";

  return (
    <div className={cn("group relative h-[280px] w-52 [perspective:1000px] cursor-pointer")}>
      {/* Delete (cross) button */}
      <button
        className={cn(
          "absolute top-2 right-0 z-50 p-1 rounded-full bg-zinc-800 text-zinc-300 transition-all duration-300 shadow-none opacity-0 pointer-events-none",
          "group-hover:opacity-100 group-hover:pointer-events-auto group-hover:scale-125 group-hover:-translate-y-2 group-hover:bg-red-600 group-hover:text-white group-hover:shadow-lg"
        )}
        onClick={e => { e.stopPropagation(); onDelete(story.story_id); }}
        title="Delete story"
        style={{ transitionProperty: 'background, color, box-shadow, transform, opacity' }}
      >
        <X size={18} />
      </button>
      {/* Back cover - static */}
      <div className={cn("absolute inset-0 h-full w-48 rounded-lg bg-zinc-900/50 shadow-md border border-zinc-800/50")}></div>
      {/* Card container with slight book opening effect on hover */}
      <div
        className={cn(
          "relative z-50 h-full w-48 origin-left transition-transform duration-500 ease-out [transform-style:preserve-3d] group-hover:[transform:rotateY(-30deg)]",
        )}
        onClick={onClick}
      >
        {/* Front side of the card */}
        <div className={cn("h-full w-full rounded-lg bg-black border-2 border-zinc-800", common)}>
          <div className="relative flex h-full w-full flex-col items-center justify-center p-6 text-center">
            {/* Inner border */}
            <div className="absolute inset-3 border rounded-md border-zinc-800/50" />
            {isLoading ? (
              <div className="flex flex-col items-center justify-center space-y-3">
                <ClassicLoader />
                <p className="text-xs text-zinc-500">Loading stories</p>
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-medium leading-tight text-zinc-400">
                  {story.title}
                </h3>
                <div className="text-xs text-zinc-600">
                  by: shakescript AI
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Sliding link/tab coming out from behind */}
      <div
        className={cn(
          "z-1 absolute bottom-0 right-0 flex h-48 w-14 -translate-x-10 transform items-start justify-start rounded-r-lg bg-emerald-600 pl-2 pt-2 text-xs font-bold text-white transition-transform duration-300 ease-in-out [backface-visibility:hidden] group-hover:translate-x-0 group-hover:rotate-[5deg]",
          isLoading ? "opacity-50" : ""
        )}
      >
        <div className="-rotate-90 whitespace-nowrap pb-16 pr-9">
          {isLoading ? "LOADING..." : "READ STORY"}
        </div>
      </div>
    </div>
  );
};

export const Library = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [selectedStory, setSelectedStory] = useState<StoryDetails | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStories, setLoadingStories] = useState(true);
  const [loadingStoryId, setLoadingStoryId] = useState<number | null>(null);
  const [currentEpisode, setCurrentEpisode] = useState(0);

  // Initialize caches
  const [storiesCache, setStoriesCache] = useState<StoryCache | null>(null);
  const [storyDetailsCache, setStoryDetailsCache] = useState<StoryDetailsCache>({});

  const [showConfirm, setShowConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; from: 'card' | 'details' } | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchStories();
  }, []);

  const fetchStories = async () => {
    // Check cache first
    if (storiesCache && Date.now() - storiesCache.timestamp < CACHE_DURATION) {
      setStories(storiesCache.data);
      setLoadingStories(false);
      return;
    }

    try {
      const response = await axios.get('http://localhost:8000/api/v1/stories/all');
      const newStories = response.data.stories;
      
      // Update cache
      setStoriesCache({
        data: newStories,
        timestamp: Date.now()
      });
      
      setStories(newStories);
    } catch (error) {
      console.error('Error fetching stories:', error);
    } finally {
      setLoadingStories(false);
    }
  };

  const handleStoryClick = async (storyId: number) => {
    // Check cache first
    if (storyDetailsCache[storyId] && Date.now() - storyDetailsCache[storyId].timestamp < CACHE_DURATION) {
      setSelectedStory(storyDetailsCache[storyId].data);
      setCurrentEpisode(0);
      return;
    }

    setLoadingStoryId(storyId);
    
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/stories/${storyId}`);
      
      if (response.data && response.data.story && response.data.story.episodes && Array.isArray(response.data.story.episodes) && response.data.story.episodes.length > 0) {
        const storyData = response.data.story;
        
        // Update cache
        setStoryDetailsCache(prev => ({
          ...prev,
          [storyId]: {
            data: storyData,
            timestamp: Date.now()
          }
        }));
        
        setSelectedStory(storyData);
        setCurrentEpisode(0);
      } else {
        console.error('Invalid story data structure:', response.data);
      }
    } catch (error) {
      console.error('Error fetching story details:', error);
    } finally {
      setLoadingStoryId(null);
    }
  };

  const nextEpisode = () => {
    if (selectedStory) {
      setCurrentEpisode((prev) => (prev + 1) % selectedStory.episodes.length);
    }
  };

  const previousEpisode = () => {
    if (selectedStory) {
      setCurrentEpisode((prev) => (prev - 1 + selectedStory.episodes.length) % selectedStory.episodes.length);
    }
  };

  const handleDownload = () => {
    if (!selectedStory) return;

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a5',
      putOnlyUsedFonts: true,
    });

    // Constants for layout
    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);

    // Title page
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(24);
    const titleLines = doc.splitTextToSize(selectedStory.title, contentWidth);
    const titleY = (pageHeight / 2) - ((titleLines.length * 10) / 2);
    
    titleLines.forEach((line: string, index: number) => {
      const y = titleY + (index * 10);
      doc.text(line, pageWidth / 2, y, { align: 'center' });
    });

    // Add "by: shakescript AI" below title
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(12);
    doc.text('by: shakescript AI', pageWidth / 2, titleY + (titleLines.length * 10) + 10, { align: 'center' });

    // Add new page after title
    doc.addPage();

    // Set font for content
    doc.setFont('times', 'normal');
    doc.setFontSize(12);

    // Add episodes
    selectedStory.episodes.forEach((episode, index) => {
      // Episode title
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.text(`Chapter ${episode.number}: ${episode.title}`, margin, margin + 10);

      // Episode content
      doc.setFont('times', 'normal');
      doc.setFontSize(12);
      const contentLines = doc.splitTextToSize(episode.content, contentWidth);
      
      let yPosition = margin + 20; // Start below episode title
      
      contentLines.forEach((line: string) => {
        // Check if we need a new page
        if (yPosition > pageHeight - margin) {
          doc.addPage();
          yPosition = margin + 10;
        }
        doc.text(line, margin, yPosition);
        yPosition += 7; // Line spacing
      });

      // Add page break after each episode except the last one
      if (index < selectedStory.episodes.length - 1) {
        doc.addPage();
      }
    });

    // Add page numbers
    const totalPages = doc.internal.pages.length - 1;
    for (let i = 2; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.text(String(i), pageWidth - margin, pageHeight - margin);
    }

    doc.save(`${selectedStory.title.toLowerCase().replace(/\s+/g, '-')}.pdf`);
  };

  const handleDelete = (storyId: number, from: 'card' | 'details') => {
    setDeleteTarget({ id: storyId, from });
    setShowConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await axios.delete(`http://localhost:8000/api/v1/stories/${deleteTarget.id}`);
      setStories(prev => prev.filter(s => s.story_id !== deleteTarget.id));
      setStoriesCache(prev => prev ? { ...prev, data: prev.data.filter(s => s.story_id !== deleteTarget.id) } : null);
      setStoryDetailsCache(prev => {
        const newCache = { ...prev };
        delete newCache[deleteTarget.id];
        return newCache;
      });
      if (selectedStory && selectedStory.story_id === deleteTarget.id) {
        setSelectedStory(null);
      }
    } catch (error) {
      alert('Failed to delete story.');
    } finally {
      setDeleting(false);
      setShowConfirm(false);
      setDeleteTarget(null);
    }
  };

  const filteredStories = stories.filter((story) =>
    story.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 bg-[#0A0A0A] p-8 overflow-y-auto">
      <ConfirmModal
        open={showConfirm}
        onConfirm={confirmDelete}
        onCancel={() => { setShowConfirm(false); setDeleteTarget(null); }}
        message={deleting ? "Deleting..." : "Are you sure you want to delete this story? This action cannot be undone."}
      />
      <div className="max-w-6xl mx-auto">
        {!selectedStory ? (
          <>
            <div className="mb-8 space-y-4">
              <h1 className="text-3xl font-bold text-zinc-100">Your Library</h1>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search stories..."
                  className="w-full pl-10 pr-4 py-3 bg-[#111111] text-zinc-100 rounded-lg border border-zinc-800 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {loadingStories ? (
              <div className="flex items-center justify-center py-12">
                <StoryCard 
                  story={{ story_id: -1, title: "" }} 
                  onClick={() => {}} 
                  isLoading={true} 
                  onDelete={() => {}} 
                />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 place-items-center">
                <AnimatePresence>
                  {filteredStories.map((story) => (
                    <motion.div
                      key={story.story_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <StoryCard 
                        story={story} 
                        onClick={() => handleStoryClick(story.story_id)} 
                        isLoading={loadingStoryId === story.story_id}
                        onDelete={(id) => handleDelete(id, 'card')}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </>
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <button
                onClick={() => setSelectedStory(null)}
                className="flex items-center gap-2 text-zinc-400 hover:text-zinc-100 transition-colors"
              >
                <ArrowLeft size={20} />
                <span>Back to Library</span>
              </button>
              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                >
                  <Download size={20} />
                  <span>Download PDF</span>
                </button>
                <button
                  onClick={() => handleDelete(selectedStory.story_id, 'details')}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <X size={20} />
                  <span>Delete</span>
                </button>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <ClassicLoader />
              </div>
            ) : (
              <div className="space-y-8">
                <div>
                  <h1 className="text-4xl font-bold text-zinc-100 mb-4">{selectedStory.title}</h1>
                  <p className="text-zinc-400">{selectedStory.summary}</p>
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
                        Episode {selectedStory.episodes[currentEpisode].number}: {selectedStory.episodes[currentEpisode].title}
                      </h2>
                      <div className="prose prose-invert max-w-none">
                        <p className="text-zinc-400 leading-relaxed">
                          {selectedStory.episodes[currentEpisode].content}
                        </p>
                      </div>
                    </motion.div>
                  </AnimatePresence>

                  {/* Navigation Buttons */}
                  <div className="flex items-center justify-between mt-6">
                    <button
                      onClick={previousEpisode}
                      disabled={selectedStory.episodes.length <= 1}
                      className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft size={20} />
                    </button>
                    
                    {/* Pagination */}
                    <div className="flex items-center gap-2">
                      {selectedStory.episodes.map((_, index) => (
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
                      disabled={selectedStory.episodes.length <= 1}
                      className="p-2 rounded-lg bg-zinc-900/50 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight size={20} />
                    </button>
                  </div>

                  {/* Episode Counter */}
                  <div className="mt-4 text-center text-sm text-zinc-500">
                    Episode {currentEpisode + 1} of {selectedStory.episodes.length}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};