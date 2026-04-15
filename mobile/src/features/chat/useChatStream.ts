// mobile/src/features/chat/useChatStream.ts
import { useCallback, useRef } from 'react';
import { useChatStore, type ChatMessage, type ToolEvent } from './chatStore';
import { createChatStream, type ChatStreamOptions } from '../../api/chat';

let toolEventIdCounter = 0;
function generateToolEventId(): string {
  return `tool_${Date.now()}_${++toolEventIdCounter}`;
}

export function useChatStream() {
  const abortRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    (content: string, knowledgeIds: string[]) => {
      console.log('[useChatStream] sendMessage called with:', { content, knowledgeIds });

      // Cancel any existing stream
      if (abortRef.current) {
        abortRef.current();
        abortRef.current = null;
      }

      const store = useChatStore.getState();
      console.log('[useChatStream] Store state - currentDialogId:', store.currentDialogId);

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
        events: [],
      };
      console.log('[useChatStream] Adding user message:', userMessage);
      store.addMessage(userMessage);

      // Create assistant placeholder
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        events: [],
      };
      console.log('[useChatStream] Adding assistant placeholder:', assistantMessage);
      store.addMessage(assistantMessage);

      // Start streaming
      store.setToolEvents([]);
      useChatStore.setState({ isStreaming: true });
      console.log('[useChatStream] Streaming started, isStreaming: true');

      const options: ChatStreamOptions = {
        dialogId: store.currentDialogId ?? undefined,
        knowledgeIds,
        enableRag: store.enableRag && knowledgeIds.length > 0,
      };
      console.log('[useChatStream] Stream options:', options);

      const { abort } = createChatStream(content, options, {
        onChunk: (chunk: string) => {
          console.log('[useChatStream] onChunk:', chunk);
        },
        onEvent: (eventType: string, data: Record<string, unknown>) => {
          console.log('[useChatStream] onEvent:', eventType, data);
          if (eventType === 'response_chunk') {
            // Backend sends: {type: "response_chunk", data: {chunk: "..."}}
            // Chunk is at data.data.chunk
            const nestedData = data.data as Record<string, unknown> | undefined;
            const accumulated = (nestedData?.accumulated || nestedData?.chunk || data.accumulated || data.chunk || '') as string;
            console.log('[useChatStream] Updating streaming message, accumulated length:', accumulated.length);
            useChatStore.getState().updateStreamingMessage(accumulated);
          } else if (eventType === 'event' || eventType === 'tool_event') {
            // Backend sends: {type: "event", data: {id, status, title, message}}
            const nestedData = data.data as Record<string, unknown> | undefined;
            const toolData = (nestedData || data) as {
              id?: string;
              status: 'START' | 'END' | 'ERROR';
              title: string;
              message: string;
            };
            const toolEvent: ToolEvent = {
              id: toolData.id || generateToolEventId(),
              type: 'tool_call',
              name: toolData.title,
              status: toolData.status,
              timestamp: new Date().toISOString(),
            };
            console.log('[useChatStream] Adding tool event:', toolEvent);
            useChatStore.getState().addToolEvent(toolEvent);
          }
        },
        onNewDialog: (dialogId: string) => {
          console.log('[useChatStream] onNewDialog:', dialogId);
          if (!useChatStore.getState().currentDialogId) {
            useChatStore.getState().setCurrentDialogId(dialogId);
            useChatStore.getState().upsertDialog({
              id: dialogId,
              title: content.slice(0, 25) + (content.length > 25 ? '...' : ''),
              updated_at: new Date().toISOString(),
            });
          }
        },
        onTitleUpdate: (title: string) => {
          console.log('[useChatStream] onTitleUpdate:', title);
          const currentId = useChatStore.getState().currentDialogId;
          if (currentId) {
            useChatStore.getState().upsertDialog({
              id: currentId,
              title,
              updated_at: new Date().toISOString(),
            });
          }
        },
        onDone: () => {
          console.log('[useChatStream] onDone - streaming finished');
          useChatStore.getState().finishStreaming();
          abortRef.current = null;
        },
        onError: (error: Error) => {
          console.error('[useChatStream] onError:', error);
          useChatStore.getState().finishStreaming();
          abortRef.current = null;
        },
      });

      abortRef.current = abort;
    },
    []
  );

  const cancelStream = useCallback(() => {
    console.log('[useChatStream] cancelStream called');
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
    }
    useChatStore.getState().finishStreaming();
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming: useChatStore((s) => s.isStreaming),
    messages: useChatStore((s) => s.messages),
    toolEvents: useChatStore((s) => s.toolEvents),
  };
}
