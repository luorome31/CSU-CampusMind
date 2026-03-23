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
export function* parseSSELines(text: string): Generator<SSEEvent> {
  const lines = text.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || !trimmed.startsWith('data: ')) continue;

    try {
      const data = JSON.parse(trimmed.slice(6));
      if (data.newDialogId) {
        yield {
          type: 'new_dialog',
          data: { dialog_id: data.newDialogId }
        };
      } else {
        yield {
          type: data.type,
          data: data.data,
          timestamp: data.timestamp,
        };
      }
    } catch {
      // Skip malformed JSON
    }
  }
}
