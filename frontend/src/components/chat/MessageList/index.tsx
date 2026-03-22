import React, { useEffect, useRef } from 'react';
import { MessageBubble } from '../MessageBubble';
import type { ChatMessage } from '../../../features/chat/chatStore';
import './MessageList.css';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

/**
 * Scrollable message list container.
 * Auto-scrolls to bottom when new messages arrive.
 */
export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isStreaming,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  if (messages.length === 0) return null;

  return (
    <div className="message-list">
      <div className="message-list-content">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
          />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default MessageList;
