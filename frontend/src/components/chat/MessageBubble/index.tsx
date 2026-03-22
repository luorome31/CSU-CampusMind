// src/components/chat/MessageBubble/index.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ToolGroup } from '../ToolGroup';
import type { ChatMessage } from '../../../features/chat/chatStore';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

/**
 * Single message bubble.
 * - User: right-aligned, dark background
 * - Assistant: left-aligned, light background, supports Markdown + tool events
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
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
            {message.events.length > 0 && <ToolGroup events={message.events} />}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;