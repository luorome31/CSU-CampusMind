import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageList } from './index';
import type { ChatMessage } from '../../../features/chat/chatStore';

describe('MessageList', () => {
  const mockMessages: ChatMessage[] = [
    {
      id: 'msg-1',
      role: 'user',
      content: 'Hello',
      events: [],
      createdAt: new Date(),
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content: 'Hi there!',
      events: [],
      createdAt: new Date(),
    },
  ];

  it('renders nothing when messages array is empty', () => {
    render(<MessageList messages={[]} isStreaming={false} />);
    expect(screen.queryByText('Hello')).not.toBeInTheDocument();
  });

  it('renders messages when provided', () => {
    render(<MessageList messages={mockMessages} isStreaming={false} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('renders multiple MessageBubble components', () => {
    render(<MessageList messages={mockMessages} isStreaming={false} />);
    const bubbles = document.querySelectorAll('.message-bubble');
    expect(bubbles.length).toBe(2);
  });

  it('applies message-list class', () => {
    render(<MessageList messages={mockMessages} isStreaming={false} />);
    const list = screen.getByText('Hello').closest('.message-list');
    expect(list).toBeInTheDocument();
  });
});
