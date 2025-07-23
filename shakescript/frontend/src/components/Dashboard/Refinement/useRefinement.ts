import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { StoryDetails, Episode } from "@/types/story";

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

export const useRefinement = ({ story, isHinglish, onComplete, initialBatch }: RefinementHookProps) => {
  // 'episodes' now holds the list of *validated* past episodes for context
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [status, setStatus] = useState<
    "loading" | "human-review" | "ai-ready" | "refining" | "complete"
  >("loading");
  const [currentBatch, setCurrentBatch] = useState<number>(initialBatch || 1);
  const [feedback, setFeedback] = useState<{ [key: number]: string }>({});
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [typingCompleted, setTypingCompleted] = useState<{
    [key: number]: boolean;
  }>({});
  // 'latestEpisode' now holds the newly generated episode that is pending review
  const [latestEpisode, setLatestEpisode] = useState<Episode | null>(null);
  const episodesEndRef = useRef<HTMLDivElement | null>(null);

  const BASE_URL = import.meta.env.VITE_BACKEND_URL;

  const progress = Math.min(
    (episodes.length / story.total_episodes) * 100,
    100,
  );

  const findLatestEpisodeInBatch = (batchEpisodes: Episode[]) => {
    return batchEpisodes.length > 0
      ? batchEpisodes.reduce((latest, current) =>
          current.episode_number > latest.episode_number ? current : latest,
        )
      : null;
  };
  
  // This function now specifically generates the *next* batch of episodes
  const generateBatch = async () => {
    setStatus("loading");
    setErrorMessage("");
    setTypingCompleted({});
    setLatestEpisode(null); // Clear the previous "latest" episode

    try {
      const response = await axios.post(
        `${BASE_URL}/api/v1/episodes/${story.story_id}/generate-batch`,
        {},
        {
          params: {
            batch_size: story.batch_size,
            hinglish: isHinglish,
            refinement_type: story.refinement_method,
          },
        },
      );

      if (response.data.status === "success") {
        const mappedEpisodes: Episode[] = response.data.episodes.map(
          (ep: any) => ({
            episode_id: ep.episode_id,
            episode_number: ep.episode_number,
            episode_title: ep.episode_title || `Episode ${ep.episode_number}`,
            episode_content: ep.episode_content,
            episode_summary: ep.episode_summary || "",
          }),
        );

        if (story.refinement_method === "AI") {
          setStatus("ai-ready");
        } else {
          setStatus("human-review");
          const initialFeedback: { [key: number]: string } = {};
          mappedEpisodes.forEach((ep: any) => {
            initialFeedback[ep.episode_number] = "";
          });
          setFeedback(initialFeedback);
        }
        // Set the new episode(s) as the "latest" for review
        setLatestEpisode(findLatestEpisodeInBatch(mappedEpisodes));
      } else {
        if (
          response.data.message &&
          response.data.message.includes("All episodes generated")
        ) {
          setStatus("complete");
          onComplete();
        } else {
          setErrorMessage(
            response.data.message || "Failed to generate episodes",
          );
        }
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to connect to the server: ${
          error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
    }
  };

  useEffect(() => {
    // Initial setup when the component loads
    const initialEpisodes: Episode[] = story.episodes.map((ep: any) => ({
      episode_id: ep.id,
      episode_number: ep.number,
      episode_title: ep.title || `Episode ${ep.number}`,
      episode_content: ep.content,
      episode_summary: ep.summary || "",
    }));
    setEpisodes(initialEpisodes);

    if (story.story_id) {
        // If there are no episodes yet, generate the first batch.
        if (initialEpisodes.length === 0) {
            generateBatch();
        } else {
            // If there are existing episodes, it means we are resuming.
            // We need to generate the *next* batch.
            generateBatch();
        }
    }
  }, [story.story_id]);

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

      if (feedbackToSubmit.length > 0) {
        const response = await axios.post(
          `${BASE_URL}/api/v1/episodes/${story.story_id}/refine-batch`,
          feedbackToSubmit,
        );

        if (response.data.status === "pending" && response.data.episodes) {
          const refinedEpisodes: Episode[] = response.data.episodes.map(
            (ep: any) => ({
              episode_id: ep.episode_id,
              episode_number: ep.episode_number,
              episode_title: ep.episode_title,
              episode_content: ep.episode_content,
              episode_summary: ep.episode_summary || "",
            }),
          );

          setLatestEpisode(findLatestEpisodeInBatch(refinedEpisodes));
          setTypingCompleted({});
          setFeedback({}); // Reset feedback
          setStatus("human-review");
        }
      } else {
        // If no feedback is submitted, just go back to the review state.
        setStatus("human-review");
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to submit feedback: ${
          error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
      setStatus("human-review"); // Revert status on error
    } finally {
      setIsSubmitting(false);
    }
  };

  const validateAndContinue = async () => {
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await axios.post(
        `${BASE_URL}/api/v1/episodes/${story.story_id}/validate-batch`,
      );

      if (response.data.status === "success") {
        // Add the validated episode to the main list
        if (latestEpisode) {
          setEpisodes((prev) => [...prev, latestEpisode]);
        }
        
        if (
          response.data.message &&
          response.data.message.includes("Story complete")
        ) {
          setStatus("complete");
          onComplete();
        } else {
          setCurrentBatch((prev) => prev + 1);
          // Generate the next batch after a short delay
          setTimeout(() => generateBatch(), 500); 
        }
      } else {
        setErrorMessage(
          response.data.message || "Failed to validate episodes",
        );
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to validate batch: ${
          error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const scrollToBottom = () => {
    episodesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return {
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
  };
};
