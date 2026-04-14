/**
 * Chat API - React Native SSE Stream Handling
 * Uses react-native-sse library for SSE support
 */

// eslint-disable-next-line @typescript-eslint/no-var-requires
const EventSource = require('react-native-sse').default;
import { storage } from '../utils/storage';
import { setUnauthorizedCallback } from './client';

export interface ChatStreamOptions {
  dialogId?: string;
  knowledgeIds: string[];
  enableRag?: boolean;
  topK?: number;
  minScore?: number;
}

export interface ChatStreamCallbacks {
  onChunk: (data: string) => void;
  onEvent: (eventType: string, data: Record<string, unknown>) => void;
  onNewDialog: (dialogId: string) => void;
  onTitleUpdate: (title: string) => void;
  onDone: () => void;
  onError: (error: Error) => void;
}

// SSE event data interface (simplified, no types from library)
interface SSEMessage {
  data: string;
  type?: string;
}

interface SSEError {
  type: string;
  message?: string;
}

/**
 * Parse SSE data line into event object.
 */
function parseSSEData(dataStr: string): Record<string, unknown> | null {
  try {
    return JSON.parse(dataStr);
  } catch {
    return null;
  }
}

/**
 * Create a chat SSE connection for React Native.
 * Uses react-native-sse which implements EventSource over XMLHttpRequest.
 */
export function createChatStream(
  message: string,
  options: ChatStreamOptions,
  callbacks: ChatStreamCallbacks
): { abort: () => void } {
  const {
    dialogId,
    knowledgeIds,
    enableRag = knowledgeIds.length > 0,
    topK = 5,
    minScore = 0.0,
  } = options;

  let es: ReturnType<typeof EventSource> | null = null;
  let aborted = false;

  const abort = () => {
    aborted = true;
    if (es) {
      es.close();
      es = null;
    }
  };

  const run = async () => {
    try {
      const token = await storage.getToken();
      const sessionId = await storage.getSessionId();

      const url = `${process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/completion/stream`;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      const body = JSON.stringify({
        message,
        dialog_id: dialogId ?? undefined,
        knowledge_ids: knowledgeIds,
        enable_rag: enableRag,
        top_k: topK,
        min_score: minScore,
      });

      console.log('[ChatAPI] Creating SSE connection to:', url);
      console.log('[ChatAPI] Request body:', body);

      es = new EventSource(url, {
        method: 'POST',
        headers,
        body,
        timeout: 0,
        pollingInterval: 0,
      });

      es.addEventListener('open', () => {
        console.log('[ChatAPI] SSE connection opened');
      });

      // Listen for message events (our SSE uses 'data:' format)
      es.addEventListener('message', (event: SSEMessage) => {
        console.log('[ChatAPI] SSE message received:', event.data);
        if (aborted) return;
        if (!event.data) return;

        const data = parseSSEData(event.data);
        if (!data) {
          console.log('[ChatAPI] Failed to parse SSE data');
          return;
        }

        console.log('[ChatAPI] Parsed SSE data:', data);

        // Check for new dialog ID
        if (data.newDialogId) {
          console.log('[ChatAPI] New dialog ID:', data.newDialogId);
          callbacks.onNewDialog(data.newDialogId as string);
          callbacks.onEvent('new_dialog', { dialog_id: data.newDialogId });
        }

        // Handle event type
        const eventType = data.type as string;
        if (eventType === 'response_chunk') {
          console.log('[ChatAPI] Response chunk:', data.chunk);
          callbacks.onChunk(data.chunk as string || '');
          callbacks.onEvent('response_chunk', data);
        } else if (eventType === 'title_update') {
          console.log('[ChatAPI] Title update:', data.title);
          callbacks.onTitleUpdate(data.title as string);
          callbacks.onEvent('title_update', data);
        } else if (eventType === 'event' || eventType === 'tool_event') {
          console.log('[ChatAPI] Tool event:', data);
          callbacks.onEvent('event', data as Record<string, unknown>);
        } else {
          console.log('[ChatAPI] Unknown event type:', eventType);
        }
      });

      // Error handling
      es.addEventListener('error', (event: SSEError) => {
        console.log('[ChatAPI] SSE error:', event);
        if (aborted) return;

        if (event.type === 'error') {
          if (event.message && event.message.includes('401')) {
            storage.clear();
            setUnauthorizedCallback(() => {});
            callbacks.onError(new Error('Unauthorized'));
            return;
          }
          callbacks.onError(new Error(event.message || 'Connection error'));
        } else if (event.type === 'exception') {
          callbacks.onError(new Error(event.message || 'Exception'));
        }
      });

    } catch (error) {
      console.log('[ChatAPI] Exception:', error);
      if (!aborted) {
        callbacks.onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  };

  run();

  return { abort };
}
