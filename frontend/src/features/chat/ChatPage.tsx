// src/features/chat/ChatPage.tsx
import React, { useCallback } from 'react';
import { EmptyState } from '../../components/chat/EmptyState';
import { KnowledgeSelector } from '../../components/chat/KnowledgeSelector';
import { MessageList } from '../../components/chat/MessageList';
import { ChatInput } from '../../components/chat/ChatInput';
import { useChatStream } from './useChatStream';
import { useChatStore } from './chatStore';
import './ChatPage.css';

// Mock knowledge bases for demo - replace with API call
const MOCK_KNOWLEDGE_BASES = [
  { id: 'kb_1', name: '教务系统' },
  { id: 'kb_2', name: '图书馆' },
  { id: 'kb_3', name: '校园通知' },
];

/**
 * Main chat page component.
 * Shows EmptyState when no messages, otherwise shows chat UI.
 */
export function ChatPage() {
  const { sendMessage, isStreaming, messages } = useChatStream();
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);

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
          <KnowledgeSelector knowledgeBases={MOCK_KNOWLEDGE_BASES} />
          <MessageList messages={messages} isStreaming={isStreaming} />
          <ChatInput onSend={handleSend} disabled={isStreaming} />
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
