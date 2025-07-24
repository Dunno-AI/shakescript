import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useState } from "react";
import { StoryDetails } from "@/types/story";
import { useAuthFetch } from '../../../lib/utils';

interface Story {
  story_id: number;
  title: string;
}

const ClassicLoader = () => {
  return (
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-emerald-500" />
  );
};

const StoryCard = ({
  story,
  onSelectStory,
  onDelete,
}: {
  story: Story;
  onSelectStory: (story: StoryDetails) => void;
  onDelete: (storyId: number) => void;
}) => {
  const common = "absolute flex w-full h-full [backface-visibility:hidden]";
  const [isLoading, setIsLoading] = useState(false);
  const BASE_URL = import.meta.env.VITE_BACKEND_URL
  const authFetch = useAuthFetch();

  const handleClick = async () => {
    if (story.story_id) {
      setIsLoading(true)
      console.log("Clicked on:", story.story_id);
      try {
        const res = await authFetch(`${BASE_URL}api/v1/stories/${story.story_id}`);
        const response = await res.json();
        if (response && response.story) {
          onSelectStory(response.story);
        }
      } catch (error) {
        alert('Failed to load story for display.');
      }
      finally{
        setIsLoading(false);
      }
    }
  };

  return (
    <div
      className={cn(
        "group relative h-[280px] w-52 [perspective:1000px] cursor-pointer",
      )}
    >
      <button
        className={cn(
          "absolute top-2 right-0 z-50 p-1 rounded-full bg-zinc-800 text-zinc-300 transition-all duration-300 shadow-none opacity-0 pointer-events-none",
          "group-hover:opacity-100 group-hover:pointer-events-auto group-hover:scale-125 group-hover:-translate-y-2 group-hover:bg-red-600 group-hover:text-white group-hover:shadow-lg",
        )}
        onClick={(e) => {
          e.stopPropagation();
          onDelete(story.story_id);
        }}
        title="Delete story"
        style={{
          transitionProperty:
            "background, color, box-shadow, transform, opacity",
        }}
      >
        <X size={18} />
      </button>
      <div
        className={cn(
          "absolute inset-0 h-full w-48 rounded-lg bg-zinc-900/50 shadow-md border border-zinc-800/50",
        )}
      ></div>
      <div
        className={cn(
          "relative z-50 h-full w-48 origin-left transition-transform duration-500 ease-out [transform-style:preserve-3d] group-hover:[transform:rotateY(-30deg)]",
        )}
        onClick={handleClick}
      >
        <div
          className={cn(
            "h-full w-full rounded-lg bg-black border-2 border-zinc-800",
            common,
          )}
        >
          <div className="relative flex h-full w-full flex-col items-center justify-center p-6 text-center">
            <div className="absolute inset-3 border rounded-md border-zinc-800/50" />
            {isLoading ? (
              <div className="flex flex-col items-center justify-center space-y-3">
                <ClassicLoader />
                <p className="text-xs text-zinc-500">Loading story</p>
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-medium leading-tight text-zinc-400">
                  {story.title}
                </h3>
                <div className="text-xs text-zinc-600">by: shakescript AI</div>
              </div>
            )}
          </div>
        </div>
      </div>
      <div
        className={cn(
          "z-1 absolute bottom-0 right-0 flex h-48 w-14 -translate-x-10 transform items-start justify-start rounded-r-lg bg-emerald-600 pl-2 pt-2 text-xs font-bold text-white transition-transform duration-300 ease-in-out [backface-visibility:hidden] group-hover:translate-x-0 group-hover:rotate-[5deg]",
          isLoading ? "opacity-50" : "",
        )}
      >
        <div className="-rotate-90 whitespace-nowrap pb-16 pr-9">
          {isLoading ? "LOADING..." : "READ STORY"}
        </div>
      </div>
    </div>
  );
};

export default StoryCard;
