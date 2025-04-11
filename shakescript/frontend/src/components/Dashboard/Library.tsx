import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Search, Download, ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
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

const ClassicLoader = () => {
  return (
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500" />
  );
};

const StoryCard = ({ 
  story, 
  onClick, 
  isLoading 
}: { 
  story: Story; 
  onClick: () => void;
  isLoading: boolean;
}) => {
  const common = "absolute flex w-full h-full [backface-visibility:hidden]";

  return (
    <div className={cn("group relative h-[280px] w-52 [perspective:1000px] cursor-pointer")} onClick={onClick}>
      {/* Back cover - static */}
      <div className={cn("absolute inset-0 h-full w-48 rounded-lg bg-zinc-900/50 shadow-md border border-zinc-800/50")}></div>

      {/* Card container with slight book opening effect on hover */}
      <div
        className={cn(
          "relative z-50 h-full w-48 origin-left transition-transform duration-500 ease-out [transform-style:preserve-3d] group-hover:[transform:rotateY(-30deg)]",
        )}
      >
        {/* Front side of the card */}
        <div className={cn("h-full w-full rounded-lg bg-black border-2 border-zinc-800", common)}>
          <div className="relative flex h-full w-full flex-col items-center justify-center p-6 text-center">
            {/* Inner border */}
            <div className="absolute inset-3 border rounded-md border-zinc-800/50" />
            
            {isLoading ? (
              <div className="flex flex-col items-center justify-center space-y-3">
                <ClassicLoader />
                <p className="text-xs text-zinc-500">Loading story...</p>
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

  useEffect(() => {
    fetchStories();
  }, []);

  const fetchStories = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/stories/all');
      setStories(response.data.stories);
    } catch (error) {
      console.error('Error fetching stories:', error);
    } finally {
      setLoadingStories(false);
    }
  };

  const handleStoryClick = async (storyId: number) => {
    // Set loading state specifically for this story card
    setLoadingStoryId(storyId);
    
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/stories/${storyId}`);
      
      // Check if the response has the expected structure
      if (response.data && response.data.story && response.data.story.episodes && Array.isArray(response.data.story.episodes) && response.data.story.episodes.length > 0) {
        setSelectedStory(response.data.story);
        setCurrentEpisode(0); // Reset episode index when selecting a new story
      } else {
        console.error('Invalid story data structure:', response.data);
        // You might want to show an error message to the user here
      }
    } catch (error) {
      console.error('Error fetching story details:', error);
      // You might want to show an error message to the user here
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

  const filteredStories = stories.filter((story) =>
    story.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 bg-[#0A0A0A] p-8 overflow-y-auto">
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
                <ClassicLoader />
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
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
              >
                <Download size={20} />
                <span>Download PDF</span>
              </button>
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