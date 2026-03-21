// src/components/chat/MessageBubble/index.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { StreamingText } from '../StreamingText';
import { ToolEventCard } from '../ToolEventCard';
import type { ChatMessage } from '../../../features/chat/chatStore';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

/**
 * Single message bubble.
 * - User: right-aligned, dark background
 * - Assistant: left-aligned, light background, supports Markdown + tool events
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false,
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-bubble message-${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : (
          <>
            <div className="message-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
            {message.events.length > 0 && (
              <div className="message-events">
                {message.events.map((event) => (
                  <ToolEventCard key={event.id} event={event} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;