/**
 * MessageList Component Tests
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react-native';
import { Text } from 'react-native';
import { MessageList } from './MessageList';
import type { ChatMessage } from '../../../features/chat/chatStore';

// Mock MessageBubble component
jest.mock('../MessageBubble', () => {
  const { Text } = require('react-native');
  return {
    MessageBubble: jest.fn(({ message }: { message: ChatMessage }) => (
      <Text testID={`message-bubble-${message.id}`}>{message.content}</Text>
    )),
  };
});

// Mock react-native-markdown-display in MessageBubble
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children }: { children: string }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

describe('MessageList Component', () => {
  const mockMessages: ChatMessage[] = [
    {
      id: '1',
      role: 'user',
      content: 'Hello, assistant!',
      created_at: '2024-01-01T00:00:00Z',
      events: [],
    },
    {
      id: '2',
      role: 'assistant',
      content: 'Hello, user! How can I help?',
      created_at: '2024-01-01T00:00:01Z',
      events: [],
    },
    {
      id: '3',
      role: 'user',
      content: 'What is 2+2?',
      created_at: '2024-01-01T00:00:02Z',
      events: [],
    },
    {
      id: '4',
      role: 'assistant',
      content: '2+2 equals 4.',
      created_at: '2024-01-01T00:00:03Z',
      events: [],
    },
  ];

  describe('Rendering', () => {
    it('should render message list container', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      expect(screen.getByTestId('message-list')).toBeTruthy();
    });

    it('should render FlatList component via container', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      // FlatList is rendered inside the container
      const container = screen.getByTestId('message-list');
      expect(container).toBeTruthy();
    });

    it('should render all messages via MessageBubble', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      expect(screen.getByTestId('message-bubble-1')).toBeTruthy();
      expect(screen.getByTestId('message-bubble-2')).toBeTruthy();
      expect(screen.getByTestId('message-bubble-3')).toBeTruthy();
      expect(screen.getByTestId('message-bubble-4')).toBeTruthy();
    });

    it('should render user message content correctly', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      expect(screen.getByText('Hello, assistant!')).toBeTruthy();
    });

    it('should render assistant message content correctly', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      expect(screen.getByText('Hello, user! How can I help?')).toBeTruthy();
    });

    it('should render empty list without crashing', () => {
      render(<MessageList messages={[]} isStreaming={false} />);

      expect(screen.getByTestId('message-list')).toBeTruthy();
    });
  });

  describe('Props Handling', () => {
    it('should accept messages prop correctly', () => {
      const { rerender } = render(
        <MessageList messages={mockMessages} isStreaming={false} />
      );

      expect(screen.getByText('Hello, assistant!')).toBeTruthy();
      expect(screen.getByText('Hello, user! How can I help?')).toBeTruthy();

      // Rerender with fewer messages
      rerender(
        <MessageList
          messages={mockMessages.slice(0, 2)}
          isStreaming={false}
        />
      );

      expect(screen.getByText('Hello, assistant!')).toBeTruthy();
      expect(screen.queryByText('What is 2+2?')).toBeNull();
    });

    it('should accept isStreaming prop without crashing', () => {
      render(<MessageList messages={mockMessages} isStreaming={true} />);

      expect(screen.getByTestId('message-list')).toBeTruthy();
    });

    it('should handle isStreaming=false state', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      expect(screen.getByTestId('message-list')).toBeTruthy();
    });
  });

  describe('Message Order', () => {
    it('should render messages in correct order', () => {
      render(<MessageList messages={mockMessages} isStreaming={false} />);

      const messageBubbles = screen.getAllByTestId(/^message-bubble-/);
      expect(messageBubbles).toHaveLength(4);

      // Check order by content
      const messageContents = messageBubbles.map((el) => el.children[0]);
      expect(messageContents[0]).toBe('Hello, assistant!');
      expect(messageContents[1]).toBe('Hello, user! How can I help?');
      expect(messageContents[2]).toBe('What is 2+2?');
      expect(messageContents[3]).toBe('2+2 equals 4.');
    });

    it('should handle single message', () => {
      const singleMessage: ChatMessage[] = [
        {
          id: '1',
          role: 'user',
          content: 'Single message',
          created_at: '2024-01-01T00:00:00Z',
          events: [],
        },
      ];

      render(<MessageList messages={singleMessage} isStreaming={false} />);

      expect(screen.getByText('Single message')).toBeTruthy();
    });

    it('should handle many messages', () => {
      const manyMessages: ChatMessage[] = Array.from({ length: 20 }, (_, i) => ({
        id: `${i}`,
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}`,
        created_at: `2024-01-01T00:00:${i.toString().padStart(2, '0')}Z`,
        events: [],
      }));

      render(<MessageList messages={manyMessages} isStreaming={false} />);

      // FlatList uses virtualization, so only visible items are rendered
      expect(screen.getByText('Message 0')).toBeTruthy();
      // Should not crash with many messages
      expect(screen.getByTestId('message-list')).toBeTruthy();
    });
  });

  describe('MessageBubble Integration', () => {
    it('should render user messages correctly', () => {
      const userMessages: ChatMessage[] = [
        {
          id: '1',
          role: 'user',
          content: 'User message content',
          created_at: '2024-01-01T00:00:00Z',
          events: [],
        },
      ];

      render(<MessageList messages={userMessages} isStreaming={false} />);

      expect(screen.getByTestId('message-bubble-1')).toBeTruthy();
      expect(screen.getByText('User message content')).toBeTruthy();
    });

    it('should render assistant messages correctly', () => {
      const assistantMessages: ChatMessage[] = [
        {
          id: '1',
          role: 'assistant',
          content: 'Assistant response',
          created_at: '2024-01-01T00:00:00Z',
          events: [],
        },
      ];

      render(<MessageList messages={assistantMessages} isStreaming={false} />);

      expect(screen.getByTestId('message-bubble-1')).toBeTruthy();
      expect(screen.getByText('Assistant response')).toBeTruthy();
    });
  });
});