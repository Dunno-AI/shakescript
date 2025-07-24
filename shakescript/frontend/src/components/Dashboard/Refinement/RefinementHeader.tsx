import { ArrowLeft } from "lucide-react";

interface RefinementHeaderProps {
  status: "loading" | "human-review" | "ai-ready" | "refining" | "complete";
  currentBatch: number;
  progress: number;
  episodesCount: number;
  totalEpisodes: number;
  storyTitle: String;
  onBack: () => void;
}

export const RefinementHeader: React.FC<RefinementHeaderProps> = ({
  status,
  currentBatch,
  progress,
  episodesCount,
  totalEpisodes,
  storyTitle,
  onBack,
}) => {
  const getTitle = () => {
    switch (status) {
      case "complete":
        return "Story Generation Complete!";
      case "refining":
        return "Refining Episodes...";
      default:
        return `Generating Episode: ${currentBatch} of ${storyTitle}`;
    }
  };

  return (
    <div className="bg-[#111111] border-b border-zinc-800 sticky top-0 z-10">
      <div className="px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </button>
          <h1 className="text-2xl font-semibold text-zinc-100">{getTitle()}</h1>
        </div>
      </div>

      <div className="px-6 pb-4">
        <div className="w-full bg-zinc-800 rounded-full h-3">
          <div
            className="bg-emerald-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-sm text-zinc-400 mt-2">
          <span>
            {episodesCount} of {totalEpisodes} episodes
          </span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>
    </div>
  );
};
