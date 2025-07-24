import React from "react";
import { PenLine } from "lucide-react";
import { Episode } from "@/types/story";
import { TypingAnimation } from "../../utils/TypingAnimation";

interface EpisodeViewerProps {
  previousEpisodes: Episode[]; // All validated past episodes
  latestEpisode: Episode | null; // The new episode for review
  refinementType: "AI" | "HUMAN";
  feedback: { [key: number]: string };
  typingCompleted: { [key: number]: boolean };
  onFeedbackChange: (episodeNumber: number, value: string) => void;
  onTypingComplete: (episodeNumber: number) => void;
  scrollToBottom: () => void;
  episodesEndRef: React.RefObject<HTMLDivElement | null>;
}

export const EpisodeViewer: React.FC<EpisodeViewerProps> = ({
  previousEpisodes,
  latestEpisode,
  refinementType,
  feedback,
  typingCompleted,
  onFeedbackChange,
  onTypingComplete,
  scrollToBottom,
  episodesEndRef,
}) => {
  return (
    <div className="relative space-y-8 pb-24">
      {/* Instructions Banner */}
      {refinementType === "HUMAN" && (
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 mb-6">
          <p className="text-blue-200 font-medium mb-2">Review & Refine</p>
          <p className="text-blue-300 text-sm">
            Review the latest generated episode below. You can provide feedback
            to improve it, or accept it and continue to the next one.
          </p>
        </div>
      )}
      {refinementType === "AI" && (
        <div className="bg-emerald-900/30 border border-emerald-700 rounded-lg p-4 mb-6">
          <p className="text-emerald-200 font-medium mb-2">
            AI-Refined Episode Ready
          </p>
          <p className="text-emerald-300 text-sm">
            This episode has been automatically refined by AI. Review it and
            continue generating more episodes.
          </p>
        </div>
      )}

      {/* Render previous, read-only episodes */}
      {previousEpisodes.map((episode) => (
        <div key={episode.episode_id} className="bg-[#111111]/50 rounded-xl p-6 border border-zinc-800/50 opacity-70">
          <h3 className="text-lg font-medium text-zinc-400 mb-4">
            Episode {episode.episode_number}: {episode.episode_title}
          </h3>
          <div className="text-zinc-400 whitespace-pre-wrap leading-relaxed text-base">
            {episode.episode_content}
          </div>
        </div>
      ))}

      {/* Render the latest episode with feedback options */}
      {latestEpisode && (
        <div className="bg-[#111111] rounded-xl p-6 border border-zinc-800">
          <h3 className="text-lg font-medium text-emerald-400 mb-4">
            Episode {latestEpisode.episode_number}: {latestEpisode.episode_title}
          </h3>

          <div className="mb-6">
            {!typingCompleted[latestEpisode.episode_number] ? (
              <TypingAnimation
                text={latestEpisode.episode_content}
                speed={15}
                className="text-zinc-300 whitespace-pre-wrap leading-relaxed text-base"
                onTyping={scrollToBottom}
                onComplete={() => onTypingComplete(latestEpisode.episode_number)}
              />
            ) : (
              <div className="text-zinc-300 whitespace-pre-wrap leading-relaxed text-base">
                {latestEpisode.episode_content}
              </div>
            )}
          </div>

          {refinementType === "HUMAN" && typingCompleted[latestEpisode.episode_number] && (
            <div className="border-t border-zinc-800 pt-4">
              <div className="flex items-center mb-3">
                <PenLine className="w-4 h-4 text-zinc-400 mr-2" />
                <label className="text-sm font-medium text-zinc-400">
                  Feedback (optional)
                </label>
              </div>
              <textarea
                value={feedback[latestEpisode.episode_number] || ""}
                onChange={(e) =>
                  onFeedbackChange(latestEpisode.episode_number, e.target.value)
                }
                placeholder="Add your feedback for this episode..."
                className="w-full p-4 bg-zinc-900 text-zinc-200 rounded-lg border border-zinc-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 resize-y min-h-[100px] transition-colors"
              />
            </div>
          )}
        </div>
      )}
      
      <div ref={episodesEndRef} />
    </div>
  );
};
