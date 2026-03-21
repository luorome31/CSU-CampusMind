// src/api/chat.ts
import { apiClient } from './client';
import { parseSSELines, type SSEEvent } from '../utils/parseSSELines';

export interface ChatStreamOptions {
  dialogId?: string;
  knowledgeIds: string[];
  enableRag?: boolean;
  topK?: number;
  minScore?: number;
}

export interface ChatStreamResult {
  event: SSEEvent;
  newDialogId?: string;
}

/**
 * Create a chat SSE stream.
 * Returns a ReadableStream that yields SSE events.
 */
export function createChatStream(
  message: string,
  options: ChatStreamOptions
): ReadableStream<ChatStreamResult> {
  const {
    dialogId,
    knowledgeIds,
    enableRag = knowledgeIds.length > 0,
    topK = 5,
    minScore = 0.0,
  } = options;

  return new ReadableStream<ChatStreamResult>({
    async start(controller) {
      try {
        const response = await fetch('/api/v1/completion/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(sessionStorage.getItem('token')
              ? { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
              : {}),
          },
          body: JSON.stringify({
            message,
            dialog_id: dialogId ?? undefined,
            knowledge_ids: knowledgeIds,
            enable_rag: enableRag,
            top_k: topK,
            min_score: minScore,
          }),
        });

        // Handle new dialog ID from response headers
        const newDialogId = response.headers.get('X-Dialog-ID');

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          controller.error(new Error(error.detail || 'Stream request failed'));
          return;
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });

          for (const event of parseSSELines(chunk)) {
            controller.enqueue({ event, newDialogId: newDialogId ?? undefined });
          }
        }

        controller.close();
      } catch (err) {
        controller.error(err);
      }
    },
  });
}
