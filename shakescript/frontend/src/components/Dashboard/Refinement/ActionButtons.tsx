import React from "react";
import { Loader2, Play, PenLine } from "lucide-react";
import { Episode } from "@/types/story";

interface ActionButtonsProps {
  status: "human-review" | "ai-ready";
  refinementType: "AI" | "HUMAN";
  isSubmitting: boolean;
  onValidateAndContinue: () => void;
  onSubmitFeedback: () => void;
  latestEpisode: Episode | null;
  total_episodes: number;
  typingCompleted: { [key: number]: boolean };
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  status,
  refinementType,
  isSubmitting,
  onValidateAndContinue,
  onSubmitFeedback,
  latestEpisode,
  total_episodes,
  typingCompleted,
}) => {
  const isTyping = !!(latestEpisode && !typingCompleted[latestEpisode.episode_number]);

  return (
    <>
      {status === "human-review" && refinementType === "HUMAN" && (
        <>
          <button
            onClick={onValidateAndContinue}
            disabled={isSubmitting || isTyping}
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            {latestEpisode?.episode_number === total_episodes ? (
              <span>Complete Story</span>
            ) : (
              <span>Generate Next Episode</span>
            )}
          </button>
          <button
            onClick={onSubmitFeedback}
            disabled={isSubmitting || isTyping}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <PenLine className="w-4 h-4" />
            )}
            <span>Refine Episode</span>
          </button>
        </>
      )}

      {status === "ai-ready" && refinementType === "AI" && (
        <button
          onClick={onValidateAndContinue}
          disabled={isSubmitting || isTyping}
          className="px-8 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors text-lg font-medium"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5" />
          )}
          <span>Continue Generating</span>
        </button>
      )}
    </>
  );
};
