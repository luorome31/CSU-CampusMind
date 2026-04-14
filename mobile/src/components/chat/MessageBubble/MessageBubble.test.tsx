/**
 * MessageBubble Component Tests
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';
import { MessageBubble } from './MessageBubble';
import type { ChatMessage } from '../../../features/chat/chatStore';

// Mock Image component to handle local asset requires
jest.mock('react-native', () => {
  const ActualRN = jest.requireActual('react-native');
  return {
    ...ActualRN,
    Image: jest.fn(() => null),
  };
});

// Mock Image component to handle local asset requires
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children, style }: { children: string; style: object }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

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

    it('should render user message with plain text', () => {
      const userMessage: ChatMessage = {
        id: '2',
        role: 'user',
        content: 'Plain text message',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={userMessage} />);

      expect(screen.getByText('Plain text message')).toBeTruthy();
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

    it('should render assistant message with markdown', () => {
      const assistantMessage: ChatMessage = {
        id: '4',
        role: 'assistant',
        content: '# Heading\nThis is **bold** text',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={assistantMessage} />);

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });

    it('should render assistant message with code', () => {
      const assistantMessage: ChatMessage = {
        id: '5',
        role: 'assistant',
        content: 'Here is some code:\n```js\nconst x = 1;\n```',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={assistantMessage} />);

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

    it('should handle special characters', () => {
      const specialCharMessage: ChatMessage = {
        id: '8',
        role: 'assistant',
        content: 'Message with <>&"\' characters',
        created_at: '2024-01-01T00:00:00Z',
        events: [],
      };

      render(<MessageBubble message={specialCharMessage} />);

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });
  });
});
