import { useState, useEffect, useCallback } from "react";
import { StoryDetails, Episode } from "@/types/story";
import { useAuthFetch } from "@/lib/utils";
import toast from "react-hot-toast"; // Import toast

interface RefinementHookProps {
  story: StoryDetails;
  isHinglish: boolean;
  onComplete: () => void;
  initialBatch?: number;
}

interface Feedback {
  episode_number: number;
  feedback: string;
}

export const useRefinement = ({
  story,
  isHinglish,
  onComplete,
  initialBatch,
}: RefinementHookProps) => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [status, setStatus] = useState<
    "loading" | "human-review" | "ai-ready" | "refining" | "complete"
  >("loading");
  const [currentBatchEpisodes, setCurrentBatchEpisodes] = useState<Episode[]>(
    [],
  );
  const [feedback, setFeedback] = useState<{ [key: number]: string }>({});
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [typingCompleted, setTypingCompleted] = useState<{
    [key: number]: boolean;
  }>({});
  const authFetch = useAuthFetch();
  const BASE_URL = import.meta.env.VITE_BACKEND_URL;

  const progress = Math.min(
    (episodes.length / story.total_episodes) * 100,
    100,
  );
  const isStoryComplete = episodes.length >= story.total_episodes;

  const generateBatch = useCallback(async () => {
    setStatus("loading");
    setErrorMessage("");
    setTypingCompleted({});

    try {
      const response = await authFetch(
        `${BASE_URL}/api/v1/episodes/${story.story_id}/generate-batch`,
        {
          method: "POST",
          body: JSON.stringify({
            batch_size: story.batch_size,
            hinglish: isHinglish,
            refinement_type: story.refinement_method,
          }),
        },
      );

      // Check for rate limit error before trying to parse JSON
      if (response.status === 429) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Rate limit exceeded.");
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.episodes && data.episodes.length > 0) {
        const newBatch: Episode[] = data.episodes;
        setCurrentBatchEpisodes(newBatch);
        if (story.refinement_method === "AI") setStatus("ai-ready");
        else setStatus("human-review");
      } else {
        setStatus("complete");
        onComplete();
      }
    } catch (error: any) {
      // --- FIX: Show a user-friendly toast notification for rate limit errors ---
      toast.error(error.message || "An unexpected error occurred.");
      setErrorMessage(error.message);
      setStatus("human-review"); // Stop the loading spinner and show buttons again
    }
  }, [
    story.story_id,
    story.batch_size,
    story.refinement_method,
    isHinglish,
    authFetch,
    onComplete,
  ]);

  useEffect(() => {
    setEpisodes(story.episodes);
    if (story.story_id && story.episodes.length < story.total_episodes) {
      generateBatch();
    } else if (story.episodes.length >= story.total_episodes) {
      setStatus("complete");
    }
  }, [story.story_id, story.episodes, story.total_episodes, generateBatch]);

  const handleFeedbackChange = (episodeNumber: number, value: string) => {
    setFeedback((prev) => ({ ...prev, [episodeNumber]: value }));
  };

  const handleTypingComplete = (episodeNumber: number) => {
    setTypingCompleted((prev) => ({ ...prev, [episodeNumber]: true }));
  };

  const submitFeedback = async () => {
    setIsSubmitting(true);
    setStatus("refining");
    setErrorMessage("");

    try {
      const feedbackToSubmit: Feedback[] = Object.entries(feedback)
        .filter(([_, text]) => text.trim().length > 0)
        .map(([episodeNumber, text]) => ({
          episode_number: parseInt(episodeNumber),
          feedback: text,
        }));

      const response = await authFetch(
        `${BASE_URL}/api/v1/episodes/${story.story_id}/refine-batch`,
        { method: "POST", body: JSON.stringify(feedbackToSubmit) },
      );
      const data = await response.json();

      if (data.episodes) {
        const refinedEpisodes: Episode[] = data.episodes;
        setCurrentBatchEpisodes(refinedEpisodes);
        setTypingCompleted({});
        setFeedback({});
        setStatus("human-review");
      }
    } catch (error: any) {
      setErrorMessage(`Failed to submit feedback: ${error.message}.`);
      setStatus("human-review");
    } finally {
      setIsSubmitting(false);
    }
  };

  const validateAndContinue = async () => {
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await authFetch(
        `${BASE_URL}/api/v1/episodes/${story.story_id}/validate-batch`,
        { method: "POST" },
      );
      const data = await response.json();

      if (data.status === "success") {
        setEpisodes((prev) => [...prev, ...currentBatchEpisodes]);

        if (data.message && data.message.includes("Story complete")) {
          setStatus("complete");
          onComplete();
        } else {
          generateBatch();
        }
      } else {
        setErrorMessage(data.message || "Failed to validate episodes");
        setStatus("human-review");
      }
    } catch (error: any) {
      setErrorMessage(`Failed to validate batch: ${error.message}.`);
      setStatus("human-review");
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    status,
    episodes,
    currentBatchEpisodes,
    progress,
    errorMessage,
    isSubmitting,
    feedback,
    typingCompleted,
    isStoryComplete,
    handleFeedbackChange,
    handleTypingComplete,
    submitFeedback,
    validateAndContinue,
  };
};
