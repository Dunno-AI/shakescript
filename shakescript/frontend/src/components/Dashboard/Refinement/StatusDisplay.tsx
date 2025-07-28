import { Check, Loader2 } from "lucide-react";
import { TypingAnimation } from "../../utils/TypingAnimation";
import { SpinLoading } from "respinner";

interface StatusDisplayProps {
  status: "loading" | "refining" | "complete";
}

export const StatusDisplay: React.FC<StatusDisplayProps> = ({ status }) => {
  if (status === "loading") {
    return (
      <div className="relative flex flex-col items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500 mb-8" />
        <TypingAnimation
          text="Generating episodes..."
          speed={30}
          className="text-zinc-300 text-xl"
        />
        <div className="text-zinc-500 text-center mt-2">
          <p>This may take a few moments...</p>
        </div> */}
        <SpinLoading fill="#777" borderRadius={4} count={12} />
      </div>
    );
  }

  if (status === "refining") {
    return (
      <div className="relative flex flex-col items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500 mb-8" />
        <TypingAnimation
          text="Refining episodes based on your feedback..."
          speed={30}
          className="text-zinc-300 text-xl"
        />
        <div className="text-zinc-500 text-center mt-2">
          <p>Please wait while we improve the episodes...</p>
        </div>
      </div>
    );
  }

  if (status === "complete") {
    return (
      <div className="relative flex flex-col items-center justify-center h-96">
        <Check className="w-16 h-16 text-emerald-500 mb-6" />
        <p className="text-2xl font-medium text-zinc-200 mb-3">
          All episodes generated successfully!
        </p>
        <p className="text-zinc-400 text-lg">
          You can now read your complete story.
        </p>
      </div>
    );
  }

  return null;
};