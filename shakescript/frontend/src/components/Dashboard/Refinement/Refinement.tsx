import React from "react";
import { StoryDetails } from "@/types/story";
import { useRefinement } from "./useRefinement";
import { RefinementHeader } from "./RefinementHeader";
import { StatusDisplay } from "./StatusDisplay";
import { EpisodeViewer } from "./EpisodeViewer";
import { ActionButtons } from "./ActionButtons";

interface RefinementProps {
  story: StoryDetails;
  isHinglish: boolean;
  onComplete: () => void;
  onBack: () => void;
  initialBatch?: number;
}

export const Refinement: React.FC<RefinementProps> = (props) => {
  const {
    status,
    currentBatch,
    episodes,
    latestEpisode,
    progress,
    errorMessage,
    isSubmitting,
    feedback,
    typingCompleted,
    episodesEndRef,
    handleFeedbackChange,
    handleTypingComplete,
    submitFeedback,
    validateAndContinue,
    scrollToBottom,
  } = useRefinement(props);

  const isReviewing = status === "human-review" || status === "ai-ready";
  const isLoadingState =
    status === "loading" || status === "refining" || status === "complete";

  return (
    <div className="h-full bg-black text-zinc-100 flex flex-col">
      <RefinementHeader
        status={status}
        currentBatch={currentBatch}
        onBack={props.onBack}
        progress={progress}
        episodesCount={episodes.length}
        totalEpisodes={props.story.total_episodes}
        storyTitle={props.story.title}
      />

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-8">
          {isLoadingState && <StatusDisplay status={status} />}

          {isReviewing && (
            <EpisodeViewer
              previousEpisodes={episodes} // Pass the validated episodes here
              latestEpisode={latestEpisode}
              refinementType={props.story.refinement_method}
              feedback={feedback}
              typingCompleted={typingCompleted}
              onFeedbackChange={handleFeedbackChange}
              onTypingComplete={handleTypingComplete}
              scrollToBottom={scrollToBottom}
              episodesEndRef={episodesEndRef}
            />
          )}

          {errorMessage && (
            <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-200">
              <p className="font-medium mb-1">Error occurred:</p>
              <p>{errorMessage}</p>
            </div>
          )}
        </div>
      </div>

      {isReviewing && latestEpisode && (
        <ActionButtons
          status={status}
          refinementType={props.story.refinement_method}
          isSubmitting={isSubmitting}
          onValidateAndContinue={validateAndContinue}
          onSubmitFeedback={submitFeedback}
        />
      )}
    </div>
  );
};
