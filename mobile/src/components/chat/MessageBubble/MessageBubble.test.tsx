/**
 * MessageBubble Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { MessageBubble } from './MessageBubble';
import type { ChatMessage } from '../../../features/chat/chatStore';

// Mock react-native-markdown-display
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children }: { children: string }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

// Mock lucide-react-native icons
jest.mock('lucide-react-native', () => ({
  Brain: () => null,
  Wrench: () => null,
}));

describe('MessageBubble Component', () => {
  describe('User Message', () => {
    it('should render user message content', () => {
      const userMessage: ChatMessage = {
        id: '1',
        role: 'user',
        content: 'Hello, this is a user message',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={userMessage} />);

      expect(screen.getByText('Hello, this is a user message')).toBeTruthy();
    });
  });

  describe('Assistant Message', () => {
    it('should render assistant message content', () => {
      const assistantMessage: ChatMessage = {
        id: '3',
        role: 'assistant',
        content: 'Hello, I am an assistant',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={assistantMessage} />);

      // Assistant messages render through Markdown
      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });
  });

  describe('Different Message Types', () => {
    it('should handle empty content', () => {
      const emptyMessage: ChatMessage = {
        id: '6',
        role: 'user',
        content: '',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={emptyMessage} />);

      // Should not crash
      expect(screen.toJSON()).toBeTruthy();
    });

    it('should handle multiline content', () => {
      const multilineMessage: ChatMessage = {
        id: '7',
        role: 'user',
        content: 'Line 1\nLine 2\nLine 3',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={multilineMessage} />);

      expect(screen.getByText('Line 1\nLine 2\nLine 3')).toBeTruthy();
    });
  });
});
