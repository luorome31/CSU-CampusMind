// src/features/chat/ChatPage.tsx
import { useCallback } from 'react';
import { EmptyState } from '../../components/chat/EmptyState';
import { MessageList } from '../../components/chat/MessageList';
import { ChatInput } from '../../components/chat/ChatInput';
import { useChatStream } from './useChatStream';
import { chatStore } from './chatStore';
import './ChatPage.css';

/**
 * Main chat page component.
 * Shows EmptyState when no messages, otherwise shows chat UI.
 */
export function ChatPage() {
  const { sendMessage, isStreaming, messages } = useChatStream();
  const currentKnowledgeIds = chatStore((s) => s.currentKnowledgeIds);

  const handleSend = useCallback(
    (content: string) => {
      sendMessage(content, currentKnowledgeIds);
    },
    [sendMessage, currentKnowledgeIds]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-page">
      {hasMessages ? (
        <>
          <MessageList messages={messages} isStreaming={isStreaming} />
          <div className="chat-page-input-fixed">
            <ChatInput onSend={handleSend} disabled={isStreaming} />
          </div>
        </>
      ) : (
        <>
          <EmptyState />
          <div className="chat-page-input-fixed">
            <ChatInput onSend={handleSend} disabled={isStreaming} />
          </div>
        </>
      )}
    </div>
  );
}
