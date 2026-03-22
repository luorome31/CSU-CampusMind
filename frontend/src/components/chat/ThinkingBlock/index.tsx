import { useState } from 'react';
import './ThinkingBlock.css';

interface ThinkingBlockProps {
  content: string;
}

export function ThinkingBlock({ content }: ThinkingBlockProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="thinking-block">
      <div
        className="thinking-block-summary"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsExpanded(!isExpanded)}
      >
        <span>{isExpanded ? '▼' : '▶'}</span>
        <span>AI 思考过程</span>
      </div>
      {isExpanded && <div className="thinking-block-body">{content}</div>}
    </div>
  );
}
