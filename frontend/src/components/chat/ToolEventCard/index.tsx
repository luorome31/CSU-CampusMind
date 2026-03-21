// src/components/chat/ToolEventCard/index.tsx
import React, { useState } from 'react';
import { ChevronDown, Loader2, CheckCircle, XCircle } from 'lucide-react';
import type { ToolEvent } from '../../../features/chat/chatStore';
import './ToolEventCard.css';

interface ToolEventCardProps {
  event: ToolEvent;
}

/**
 * Expandable tool event card shown within assistant messages.
 * Shows status icon, title, and brief message.
 * Clicking expands to show full details.
 */
export const ToolEventCard: React.FC<ToolEventCardProps> = ({ event }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusIcon = {
    START: <Loader2 size={14} className="tool-icon tool-icon-loading" />,
    END: <CheckCircle size={14} className="tool-icon tool-icon-success" />,
    ERROR: <XCircle size={14} className="tool-icon tool-icon-error" />,
  }[event.status];

  const statusText = {
    START: '进行中',
    END: '完成',
    ERROR: '错误',
  }[event.status];

  return (
    <div
      className={`tool-event-card tool-event-${event.status.toLowerCase()}`}
    >
      <button
        className="tool-event-header"
        onClick={() => setIsExpanded(!isExpanded)}
        type="button"
      >
        <div className="tool-event-summary">
          {statusIcon}
          <span className="tool-event-title">{event.title}</span>
          <span className="tool-event-status">{statusText}</span>
        </div>
        <ChevronDown
          size={14}
          className={`tool-event-chevron ${isExpanded ? 'expanded' : ''}`}
        />
      </button>
      {isExpanded && (
        <div className="tool-event-details">
          <p className="tool-event-message">{event.message}</p>
        </div>
      )}
    </div>
  );
};

export default ToolEventCard;