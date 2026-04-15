/**
 * Chat API - React Native SSE Stream Handling
 * Uses native XMLHttpRequest to properly handle stream termination
 */

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

/**
 * Handle events dynamically
 */
function handleEventData(dataStr: string, callbacks: ChatStreamCallbacks) {
  try {
    const data = JSON.parse(dataStr);
    
    // Check for new dialog ID
    if (data.newDialogId) {
      console.log('[ChatAPI] New dialog ID:', data.newDialogId);
      callbacks.onNewDialog(data.newDialogId as string);
      callbacks.onEvent('new_dialog', { dialog_id: data.newDialogId });
      return;
    }

    // Unwrap if double-wrapped
    let eventType = data.type || data.event_type;
    let payload = data.data || data;

    if (data.data && typeof data.data === 'object' && (data.type || data.event_type)) {
      eventType = data.type || data.event_type;
      payload = data.data;
    }

    if (eventType === 'response_chunk') {
      const chunk = (payload?.chunk || payload?.accumulated || data.chunk || data.accumulated || '') as string;
      callbacks.onChunk(chunk);
      callbacks.onEvent('response_chunk', data);
    } else if (eventType === 'title_update') {
      const title = (payload?.title || data.title) as string;
      console.log('[ChatAPI] Title update:', title);
      callbacks.onTitleUpdate(title);
      callbacks.onEvent('title_update', data);
    } else if (eventType === 'event' || eventType === 'tool_event') {
      console.log('[ChatAPI] Tool event:', data);
      callbacks.onEvent('event', data as Record<string, unknown>);
    } else {
      console.log('[ChatAPI] Unknown event type:', eventType);
    }
  } catch (err) {
    console.log('[ChatAPI] Failed to parse SSE data:', dataStr);
  }
}

/**
 * Create a chat SSE connection for React Native using native XMLHttpRequest.
 * This correctly detects when the server closes the stream, 
 * unlike react-native-sse which swallows the EOF to auto-reconnect.
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

  let xhr: XMLHttpRequest | null = null;
  let aborted = false;

  const abort = () => {
    aborted = true;
    if (xhr) {
      xhr.abort();
      xhr = null;
    }
  };

  const run = async () => {
    try {
      const token = await storage.getToken();
      const sessionId = await storage.getSessionId();

      const url = `${process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/completion/stream`;

      xhr = new XMLHttpRequest();
      xhr.open('POST', url, true);
      
      xhr.setRequestHeader('Content-Type', 'application/json');
      if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      if (sessionId) xhr.setRequestHeader('X-Session-ID', sessionId);
      xhr.setRequestHeader('Accept', 'text/event-stream');

      const body = JSON.stringify({
        message,
        dialog_id: dialogId ?? undefined,
        knowledge_ids: knowledgeIds,
        enable_rag: enableRag,
        top_k: topK,
        min_score: minScore,
      });

      console.log('[ChatAPI] Creating native XHR SSE connection to:', url);

      let processedLength = 0;
      let lineBuffer = '';

      xhr.onreadystatechange = () => {
        if (aborted || !xhr) return;

        // Process incoming chunks
        if (xhr.readyState === XMLHttpRequest.LOADING || xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status >= 200 && xhr.status < 400 && xhr.responseText) {
            const newText = xhr.responseText.substring(processedLength);
            if (newText) {
              processedLength = xhr.responseText.length;
              lineBuffer += newText;

              const parts = lineBuffer.split(/\r?\n/);
              // The last part is either incomplete or empty string if it ended neatly at newline
              lineBuffer = parts.pop() || '';

              for (const line of parts) {
                const trimmed = line.trim();
                // Standard SSE messages start with data:
                if (!trimmed || !trimmed.startsWith('data: ')) continue;
                
                const dataStr = trimmed.slice(6).trim();
                if (dataStr === '[DONE]') {
                  continue; // Server optional explicit done
                }
                handleEventData(dataStr, callbacks);
              }
            }
          }
        }

        // Handle termination
        if (xhr.readyState === XMLHttpRequest.DONE) {
          console.log('[ChatAPI] XHR done, status:', xhr.status);
          
          // Process trailing buffer data if exists
          const finalTrimmed = lineBuffer.trim();
          if (finalTrimmed && finalTrimmed.startsWith('data: ')) {
             const dataStr = finalTrimmed.slice(6).trim();
             if (dataStr !== '[DONE]') {
                 handleEventData(dataStr, callbacks);
             }
          }

          if (xhr.status >= 200 && xhr.status < 400) {
            callbacks.onDone();
          } else if (xhr.status === 401) {
            storage.clear();
            setUnauthorizedCallback(() => {});
            callbacks.onError(new Error('Unauthorized'));
          } else if (xhr.status === 0 && !aborted) {
            callbacks.onError(new Error('Network error or server disconnected'));
          } else if (!aborted) {
            callbacks.onError(new Error(`HTTP Error ${xhr.status}: ${xhr.responseText}`));
          }
        }
      };

      xhr.onerror = () => {
        if (!aborted) {
          callbacks.onError(new Error('XMLHttpRequest Network Error'));
        }
      };

      xhr.send(body);

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
