import { useState, useEffect, useRef } from "react";
import { StoryDetails, Episode } from "@/types/story";
import { useAuthFetch } from "@/lib/utils";

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
  const [currentBatch, setCurrentBatch] = useState<number>(initialBatch || 1);
  const [feedback, setFeedback] = useState<{ [key: number]: string }>({});
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [typingCompleted, setTypingCompleted] = useState<{
    [key: number]: boolean;
  }>({});
  const [latestEpisode, setLatestEpisode] = useState<Episode | null>(null);
  const [userHasScrolled, setUserHasScrolled] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const episodesEndRef = useRef<HTMLDivElement | null>(null);
  const authFetch = useAuthFetch();

  const BASE_URL = import.meta.env.VITE_BACKEND_URL;

  const progress = Math.min(
    ((episodes.length+1) / story.total_episodes) * 100,
    100,
  );

  const findLatestEpisodeInBatch = (batchEpisodes: Episode[]) => {
    return batchEpisodes.length > 0
      ? batchEpisodes.reduce((latest, current) =>
        current.episode_number > latest.episode_number ? current : latest,
      )
      : null;
  };

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      const handleScroll = () => {
        const { scrollTop, scrollHeight, clientHeight } = container;
        const atBottom = scrollHeight - scrollTop <= clientHeight + 1;
        setUserHasScrolled(!atBottom);
      };
      container.addEventListener("scroll", handleScroll);
      return () => container.removeEventListener("scroll", handleScroll);
    }
  }, [scrollContainerRef.current]);

  const scrollToBottom = () => {
    if (episodesEndRef.current && !userHasScrolled) {
      episodesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const manualScrollToBottom = () => {
    if (episodesEndRef.current) {
      episodesEndRef.current.scrollIntoView({ behavior: "smooth" });
      setUserHasScrolled(false);
    }
  };

  const generateBatch = async () => {
    setStatus("loading");
    setErrorMessage("");
    setTypingCompleted({});
    setLatestEpisode(null);

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

      const data = await response.json();

      if (data.status === "success") {
        const mappedEpisodes: Episode[] = data.episodes.map((ep: any) => ({
          episode_id: ep.episode_id,
          episode_number: ep.episode_number,
          episode_title: ep.episode_title || `Episode ${ep.episode_number}`,
          episode_content: ep.episode_content,
          episode_summary: ep.episode_summary || "",
        }));

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
        setLatestEpisode(findLatestEpisodeInBatch(mappedEpisodes));
      } else {
        if (data.message && data.message.includes("All episodes generated")) {
          setStatus("complete");
          onComplete();
        } else {
          setErrorMessage(data.message || "Failed to generate episodes");
        }
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to connect to the server: ${error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
    }
  };

  useEffect(() => {
    const initialEpisodes: Episode[] = story.episodes.map((ep: any) => ({
      episode_id: ep.id,
      episode_number: ep.number,
      episode_title: ep.title || `Episode ${ep.number}`,
      episode_content: ep.content,
      episode_summary: ep.summary || "",
    }));
    setEpisodes(initialEpisodes);

    if (story.story_id) {
      if (initialEpisodes.length === 0) {
        generateBatch();
      } else {
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
        const response = await authFetch(
          `${BASE_URL}/api/v1/episodes/${story.story_id}/refine-batch`,
          {
            method: "POST",
            body: JSON.stringify(feedbackToSubmit),
          },
        );
        const data = await response.json();

        if (data.status === "pending" && data.episodes) {
          const refinedEpisodes: Episode[] = data.episodes.map((ep: any) => ({
            episode_id: ep.episode_id,
            episode_number: ep.episode_number,
            episode_title: ep.episode_title,
            episode_content: ep.episode_content,
            episode_summary: ep.episode_summary || "",
          }));

          setLatestEpisode(findLatestEpisodeInBatch(refinedEpisodes));
          setTypingCompleted({});
          setFeedback({});
          setStatus("human-review");
        }
      } else {
        setStatus("human-review");
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to submit feedback: ${error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
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
        if (latestEpisode) {
          setEpisodes((prev) => [...prev, latestEpisode]);
        }

        if (data.message && data.message.includes("Story complete")) {
          setStatus("complete");
          onComplete();
        } else {
          setCurrentBatch((prev) => prev + 1);
          setTimeout(() => generateBatch(), 500);
        }
      } else {
        setErrorMessage(data.message || "Failed to validate episodes");
      }
    } catch (error: any) {
      setErrorMessage(
        `Failed to validate batch: ${error.response?.data?.detail || error.message || "Unknown error"
        }. Please try again.`,
      );
    } finally {
      setIsSubmitting(false);
    }
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
    scrollContainerRef,
    userHasScrolled,
    handleFeedbackChange,
    handleTypingComplete,
    submitFeedback,
    validateAndContinue,
    scrollToBottom,
    manualScrollToBottom,
  };
};
