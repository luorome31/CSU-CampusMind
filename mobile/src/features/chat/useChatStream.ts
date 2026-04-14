// mobile/src/features/chat/useChatStream.ts
import { useCallback, useRef } from 'react';
import { useChatStore, type ChatMessage, type ToolEvent } from './chatStore';
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

      try {
        const stream = createChatStream(content, {
          dialogId: store.currentDialogId ?? undefined,
          knowledgeIds,
          enableRag: store.enableRag && knowledgeIds.length > 0,
          signal: abortControllerRef.current.signal,
        });

        // RN uses async generator iteration instead of ReadableStream reader
        for await (const { event, newDialogId } of stream) {
          // Set new dialog ID from header fallback
          if (newDialogId && !useChatStore.getState().currentDialogId) {
            useChatStore.getState().setCurrentDialogId(newDialogId);
            useChatStore.getState().upsertDialog({
              id: newDialogId,
              title: content.slice(0, 25) + (content.length > 25 ? '...' : ''),
              updated_at: new Date().toISOString()
            });
          }

          if (event.type === 'new_dialog') {
            const data = event.data as { dialog_id: string };
            if (!useChatStore.getState().currentDialogId) {
              useChatStore.getState().setCurrentDialogId(data.dialog_id);
              useChatStore.getState().upsertDialog({
                id: data.dialog_id,
                title: content.slice(0, 25) + (content.length > 25 ? '...' : ''),
                updated_at: new Date().toISOString()
              });
            }
          } else if (event.type === 'response_chunk') {
            const data = event.data as { accumulated: string };
            useChatStore.getState().updateStreamingMessage(data.accumulated);
          } else if (event.type === 'event') {
            const data = event.data as { id?: string; status: 'START' | 'END' | 'ERROR'; title: string; message: string };
            const toolEvent: ToolEvent = {
              id: data.id || generateToolEventId(),
              type: 'tool_call',
              name: data.title,
              status: data.status,
              timestamp: new Date().toISOString(),
            };
            useChatStore.getState().addToolEvent(toolEvent);
          } else if (event.type === 'title_update') {
            const data = event.data as { title: string };
            const currentId = useChatStore.getState().currentDialogId;
            if (currentId) {
              useChatStore.getState().upsertDialog({
                id: currentId,
                title: data.title,
                updated_at: new Date().toISOString()
              });
            }
          }
        }
      } catch (err) {
        console.error('Stream error:', err);
      } finally {
        useChatStore.setState({ isStreaming: false });
        abortControllerRef.current = null;
      }
    },
    []
  );

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort();
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
