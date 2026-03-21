// src/components/chat/StreamingText/index.tsx
import React, { useEffect, useState } from 'react';
import './StreamingText.css';

interface StreamingTextProps {
  text: string;
  isStreaming: boolean;
}

/**
 * Animated text that reveals content as it streams in.
 * Uses cursor blinking during streaming.
 */
export const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  isStreaming,
}) => {
  const [displayedText, setDisplayedText] = useState(text);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (text === displayedText) return;

    setIsAnimating(true);

    // For simplicity, we update immediately since backend sends accumulated text
    // This component mainly handles the streaming cursor
    setDisplayedText(text);
    setIsAnimating(false);
  }, [text]);

  return (
    <span className="streaming-text">
      {displayedText}
      {isStreaming && <span className="streaming-cursor" />}
    </span>
  );
};

export default StreamingText;
