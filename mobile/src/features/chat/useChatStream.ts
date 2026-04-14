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
      // Cancel any existing stream
      if (abortRef.current) {
        abortRef.current();
        abortRef.current = null;
      }

      const store = useChatStore.getState();

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
        events: [],
      };
      store.addMessage(userMessage);

      // Create assistant placeholder
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        events: [],
      };
      store.addMessage(assistantMessage);

      // Start streaming
      store.setToolEvents([]);
      useChatStore.setState({ isStreaming: true });

      const options: ChatStreamOptions = {
        dialogId: store.currentDialogId ?? undefined,
        knowledgeIds,
        enableRag: store.enableRag && knowledgeIds.length > 0,
      };

      const { abort } = createChatStream(content, options, {
        onChunk: (_chunk: string) => {
          // Chunk is already accumulated in onEvent via response_chunk
        },
        onEvent: (eventType: string, data: Record<string, unknown>) => {
          if (eventType === 'response_chunk') {
            const accumulated = data.accumulated as string;
            useChatStore.getState().updateStreamingMessage(accumulated);
          } else if (eventType === 'event' || eventType === 'tool_event') {
            const toolData = data as unknown as {
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
            useChatStore.getState().addToolEvent(toolEvent);
          }
        },
        onNewDialog: (dialogId: string) => {
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
          useChatStore.setState({ isStreaming: false });
          abortRef.current = null;
        },
        onError: (error: Error) => {
          console.error('Stream error:', error);
          useChatStore.setState({ isStreaming: false });
          abortRef.current = null;
        },
      });

      abortRef.current = abort;
    },
    []
  );

  const cancelStream = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
    }
    useChatStore.setState({ isStreaming: false });
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming: useChatStore((s) => s.isStreaming),
    messages: useChatStore((s) => s.messages),
    toolEvents: useChatStore((s) => s.toolEvents),
  };
}
