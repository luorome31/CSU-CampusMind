// src/features/chat/useChatStream.ts
import { useCallback, useRef } from 'react';
import { chatStore, type ChatMessage, type ToolEvent } from './chatStore';
import { createChatStream, type ChatStreamResult } from '../../api/chat';

let toolEventIdCounter = 0;
function generateToolEventId(): string {
  return `tool_${Date.now()}_${++toolEventIdCounter}`;
}

export function useChatStream() {
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string, knowledgeIds: string[]) => {
      // Cancel any existing stream
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      const store = chatStore.getState();

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        events: [],
        createdAt: new Date(),
      };
      store.addMessage(userMessage);

      // Create assistant placeholder
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: '',
        events: [],
        createdAt: new Date(),
      };
      store.addMessage(assistantMessage);

      // Start streaming
      store.setToolEvents([]);
      chatStore.setState({ isStreaming: true });

      try {
        const stream = createChatStream(content, {
          dialogId: store.currentDialogId ?? undefined,
          knowledgeIds,
          enableRag: knowledgeIds.length > 0,
        });

        const reader = stream.getReader();

        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;

          const { event, newDialogId } = value as ChatStreamResult;

          // Set new dialog ID if this is a new dialog
          if (newDialogId && !store.currentDialogId) {
            chatStore.getState().setCurrentDialogId(newDialogId);
          }

          if (event.type === 'response_chunk') {
            const data = event.data as { accumulated: string };
            chatStore.getState().updateStreamingMessage(data.accumulated);
          } else if (event.type === 'event') {
            const data = event.data as { status: 'START' | 'END' | 'ERROR'; title: string; message: string };
            const toolEvent: ToolEvent = {
              id: generateToolEventId(),
              status: data.status,
              title: data.title,
              message: data.message,
            };
            chatStore.getState().addToolEvent(toolEvent);
          }
        }
      } catch (err) {
        console.error('Stream error:', err);
      } finally {
        chatStore.setState({ isStreaming: false });
        abortControllerRef.current = null;
      }
    },
    []
  );

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort();
    chatStore.setState({ isStreaming: false });
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming: chatStore((s) => s.isStreaming),
    messages: chatStore((s) => s.messages),
    toolEvents: chatStore((s) => s.toolEvents),
  };
}
