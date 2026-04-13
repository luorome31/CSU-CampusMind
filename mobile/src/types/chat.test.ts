/**
 * Chat Types Tests
 */

import { describe, it, expect } from '@jest/globals';
import type {
  ChatMessage,
  Citation,
  Dialog,
  ToolEvent,
  ThinkingBlock,
  StreamChunk,
} from './chat';

describe('Chat types', () => {
  describe('ChatMessage', () => {
    it('should accept valid user message', () => {
      const msg: ChatMessage = {
        id: '1',
        role: 'user',
        content: 'Hello',
        created_at: '2024-01-01T00:00:00Z',
      };
      expect(msg.role).toBe('user');
    });

    it('should accept assistant message with citations', () => {
      const citation: Citation = {
        index: 0,
        document_id: 'doc1',
        text: 'source text',
        score: 0.95,
      };
      const msg: ChatMessage = {
        id: '2',
        role: 'assistant',
        content: 'Answer',
        created_at: '2024-01-01T00:00:00Z',
        citations: [citation],
      };
      expect(msg.citations).toHaveLength(1);
    });
  });

  describe('Dialog', () => {
    it('should accept valid dialog', () => {
      const dialog: Dialog = {
        id: '1',
        title: 'Test Dialog',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        message_count: 5,
      };
      expect(dialog.message_count).toBe(5);
    });
  });

  describe('ToolEvent', () => {
    it('should accept tool call event', () => {
      const event: ToolEvent = {
        id: '1',
        type: 'tool_call',
        name: 'search',
        status: 'START',
        input: { query: 'test' },
        timestamp: '2024-01-01T00:00:00Z',
      };
      expect(event.status).toBe('START');
    });

    it('should accept tool error event', () => {
      const event: ToolEvent = {
        id: '2',
        type: 'tool_error',
        name: 'search',
        status: 'ERROR',
        error: 'Network failure',
        timestamp: '2024-01-01T00:00:00Z',
      };
      expect(event.error).toBe('Network failure');
    });
  });

  describe('ThinkingBlock', () => {
    it('should accept thinking block with reasoning', () => {
      const block: ThinkingBlock = {
        id: '1',
        content: 'Let me think...',
        reasoning: 'Because...',
      };
      expect(block.reasoning).toBe('Because...');
    });
  });

  describe('StreamChunk', () => {
    it('should accept message chunk', () => {
      const chunk: StreamChunk = {
        type: 'message',
        data: { content: 'Hello' },
      };
      expect(chunk.type).toBe('message');
    });

    it('should accept done chunk', () => {
      const chunk: StreamChunk = {
        type: 'done',
        data: null,
      };
      expect(chunk.type).toBe('done');
    });
  });
});
