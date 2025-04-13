import { cn } from "../../lib/utils";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: "emerald" | "purple" | "orange";
}

export const GlassCard = ({ children, className, glowColor }: GlassCardProps) => {
  return (
    <div
      className={cn(
        "glass-card rounded-xl p-6",
        {
          "glow-emerald": glowColor === "emerald",
          "glow-purple": glowColor === "purple",
          "glow-orange": glowColor === "orange",
        },
        className
      )}
    >
      {children}
    </div>
  );
}; 