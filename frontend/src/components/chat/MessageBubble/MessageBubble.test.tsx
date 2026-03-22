import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from './index';
import type { ChatMessage } from '../../../features/chat/chatStore';

describe('MessageBubble', () => {
  const userMessage: ChatMessage = {
    id: 'msg-1',
    role: 'user',
    content: 'Hello, what is my grade?',
    events: [],
    createdAt: new Date(),
  };

  const assistantMessage: ChatMessage = {
    id: 'msg-2',
    role: 'assistant',
    content: 'Your grade is A.',
    events: [],
    createdAt: new Date(),
  };

  it('renders user message content', () => {
    render(<MessageBubble message={userMessage} />);
    expect(screen.getByText('Hello, what is my grade?')).toBeInTheDocument();
  });

  it('renders assistant message content', () => {
    render(<MessageBubble message={assistantMessage} />);
    expect(screen.getByText('Your grade is A.')).toBeInTheDocument();
  });

  it('applies user-specific class for user messages', () => {
    render(<MessageBubble message={userMessage} />);
    const bubble = screen.getByText('Hello, what is my grade?').closest('.message-bubble');
    expect(bubble).toHaveClass('message-user');
  });

  it('applies assistant-specific class for assistant messages', () => {
    render(<MessageBubble message={assistantMessage} />);
    const bubble = screen.getByText('Your grade is A.').closest('.message-bubble');
    expect(bubble).toHaveClass('message-assistant');
  });

  it('renders markdown content for assistant messages', () => {
    const markdownMessage: ChatMessage = {
      ...assistantMessage,
      content: '## Header\n\n**Bold** text',
    };
    render(<MessageBubble message={markdownMessage} />);
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Header');
  });

  it('renders tool events for assistant messages', () => {
    const messageWithEvents: ChatMessage = {
      ...assistantMessage,
      events: [
        {
          id: 'event-1',
          status: 'END',
          title: 'Query JWC',
          message: 'Found grade data',
        },
      ],
    };
    render(<MessageBubble message={messageWithEvents} />);
    // ToolGroup shows summary text when collapsed
    expect(screen.getByText('执行完成 1 个工具')).toBeInTheDocument();
  });

  it('does not render tool events for user messages', () => {
    const userMsgWithEvents: ChatMessage = {
      ...userMessage,
      events: [
        {
          id: 'event-1',
          status: 'END',
          title: 'Query JWC',
          message: 'Found grade data',
        },
      ],
    };
    render(<MessageBubble message={userMsgWithEvents} />);
    expect(screen.queryByText('Query JWC')).not.toBeInTheDocument();
  });
});
