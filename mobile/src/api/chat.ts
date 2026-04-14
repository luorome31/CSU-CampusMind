/**
 * Chat API - React Native SSE Stream Handling
 * Uses fetch + response.body.getReader() pattern (RN doesn't support ReadableStream)
 */

import { storage } from '../utils/storage';
import { setUnauthorizedCallback } from './client';

export interface ChatStreamOptions {
  dialogId?: string;
  knowledgeIds: string[];
  enableRag?: boolean;
  topK?: number;
  minScore?: number;
  signal?: AbortSignal;
}

export interface ChatStreamResult {
  event: SSEEvent;
  newDialogId?: string;
}

export type SSEEventType = 'event' | 'response_chunk' | 'new_dialog' | 'title_update';

export interface SSEEvent {
  type: SSEEventType;
  data: Record<string, unknown>;
  timestamp?: number;
}

export interface SSEToolEventData {
  status: 'START' | 'END' | 'ERROR';
  title: string;
  message: string;
}

export interface SSEResponseChunkData {
  chunk: string;
  accumulated: string;
}

/**
 * Parse SSE lines from chunk text.
 * Yields individual SSE events.
 */
function* parseSSELines(text: string): Generator<SSEEvent> {
  const lines = text.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || !trimmed.startsWith('data: ')) continue;

    try {
      const data = JSON.parse(trimmed.slice(6));
      if (data.newDialogId) {
        yield {
          type: 'new_dialog' as SSEEventType,
          data: { dialog_id: data.newDialogId },
        };
      } else if (data.type === 'title_update') {
        yield {
          type: 'title_update' as SSEEventType,
          data: data.data,
          timestamp: data.timestamp,
        };
      } else {
        yield {
          type: data.type as SSEEventType,
          data: data.data,
          timestamp: data.timestamp,
        };
      }
    } catch {
      // Skip malformed JSON
    }
  }
}

/**
 * Create a chat SSE stream for React Native.
 * Uses fetch + response.body.getReader() instead of ReadableStream.
 * Returns an async generator that yields SSE events.
 */
export async function* createChatStream(
  message: string,
  options: ChatStreamOptions
): AsyncGenerator<ChatStreamResult> {
  const {
    dialogId,
    knowledgeIds,
    enableRag = knowledgeIds.length > 0,
    topK = 5,
    minScore = 0.0,
    signal,
  } = options;

  const token = await storage.getToken();
  const sessionId = await storage.getSessionId();

  const response = await fetch(
    `${process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/completion/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(sessionId ? { 'X-Session-ID': sessionId } : {}),
      },
      body: JSON.stringify({
        message,
        dialog_id: dialogId ?? undefined,
        knowledge_ids: knowledgeIds,
        enable_rag: enableRag,
        top_k: topK,
        min_score: minScore,
      }),
      signal,
    }
  );

  // Handle 401 specifically - clear tokens and trigger logout
  if (response.status === 401) {
    await storage.clear();
    setUnauthorizedCallback(() => {});
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Stream request failed');
  }

  // Get new dialog ID from response headers
  const newDialogId = response.headers.get('X-Dialog-ID') ?? undefined;

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });

      for (const event of parseSSELines(chunk)) {
        yield { event, newDialogId };
      }
    }
  } finally {
    reader.releaseLock();
  }
}
