import React, { useEffect, useState, useRef } from 'react';

interface TypingAnimationProps {
  text: string;
  speed?: number; // ms per character
  className?: string;
  onTyping?: () => void; // called on every character typed
}

const CursorSVG: React.FC = () => (
  <svg
    viewBox="8 4 8 16"
    xmlns="http://www.w3.org/2000/svg"
    className="cursor"
    style={{ width: '1ch', display: 'inline-block', marginBottom: 4 }}
  >
    <rect x="10" y="6" width="4" height="12" fill="#fff" />
  </svg>
);

// Store animation start times outside the component to persist across re-mounts
const animationStore = new Map<string, { startTime: number }>();

export const TypingAnimation: React.FC<TypingAnimationProps> = ({ text, speed = 20, className, onTyping }) => {
  // Set the start time only once for each unique text
  if (!animationStore.has(text)) {
    animationStore.set(text, { startTime: Date.now() });
  }
  const startTime = animationStore.get(text)!.startTime;

  const [displayedText, setDisplayedText] = useState('');
  const animationFrameId = useRef<number | null>(null);
  const lastTypedLength = useRef(0);

  useEffect(() => {
    const animate = () => {
      const elapsedTime = Date.now() - startTime;
      const charsToShow = Math.min(Math.floor(elapsedTime / speed), text.length);

      setDisplayedText(text.slice(0, charsToShow));

      // Trigger the callback if new characters have been "typed"
      if (onTyping && charsToShow > lastTypedLength.current) {
        onTyping();
        lastTypedLength.current = charsToShow;
      }

      // Continue the animation until the text is fully displayed
      if (charsToShow < text.length) {
        animationFrameId.current = requestAnimationFrame(animate);
      }
    };

    // Start the animation
    animationFrameId.current = requestAnimationFrame(animate);

    // Cleanup function to cancel the animation frame on unmount
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [text, speed, onTyping, startTime]);

  const isCompleted = displayedText.length === text.length;

  return (
    <span className={className} style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
      {displayedText}
      {!isCompleted && <CursorSVG />}
    </span>
  );
};