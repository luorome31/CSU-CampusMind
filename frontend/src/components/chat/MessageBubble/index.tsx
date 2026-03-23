// src/components/chat/MessageBubble/index.tsx
import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ToolGroup } from '../ToolGroup';
import { ThinkingBlock } from '../ThinkingBlock';
import type { ChatMessage } from '../../../features/chat/chatStore';
import { ASSISTANT_AVATAR } from '../../../utils/avatar';
import { parseThinkingContent } from '../../../utils/parseThinking';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

/**
 * Single message bubble.
 * - User: right-aligned, dark background
 * - Assistant: left-aligned, light background, supports Markdown + tool events + thinking process
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
}) => {
  const isUser = message.role === 'user';

  // Parse thinking content from assistant messages
  const parsedContent = useMemo(() => {
    if (isUser) return null;
    return parseThinkingContent(message.content);
  }, [message.content, isUser]);

  return (
    <div className={`message-bubble message-${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="message-avatar">
          <img src={ASSISTANT_AVATAR} alt="Assistant" />
        </div>
      )}
      <div className="message-content">
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : parsedContent ? (
          <>
            {parsedContent.thinking.length > 0 && (
              <ThinkingBlock thinking={parsedContent.thinking} />
            )}
            {parsedContent.text && (
              <div className="message-markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {parsedContent.text}
                </ReactMarkdown>
              </div>
            )}
            {message.events.length > 0 && <ToolGroup events={message.events} />}
          </>
        ) : (
          // Fallback for messages without thinking tags (legacy or simple text)
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