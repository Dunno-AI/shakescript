import React, { useEffect, useState } from 'react';

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

export const TypingAnimation: React.FC<TypingAnimationProps> = ({ text, speed = 20, className, onTyping }) => {
  const [displayed, setDisplayed] = useState('');
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setCompleted(false);
    let i = 0;
    const intervalId = setInterval(() => {
      setDisplayed(text.slice(0, i));
      if (onTyping) onTyping();
      i++;
      if (i > text.length) {
        clearInterval(intervalId);
        setCompleted(true);
      }
    }, speed);
    return () => clearInterval(intervalId);
  }, [text, speed, onTyping]);

  return (
    <span className={className} style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
      {displayed}
      {!completed && <CursorSVG />}
    </span>
  );
};

// CSS for cursor animation
// Add this to your global CSS or import in your component
// .cursor {
//   animation: flicker 0.5s infinite;
// }
// @keyframes flicker {
//   0% { opacity: 0; }
//   50% { opacity: 1; }
//   100% { opacity: 0; }
// } 