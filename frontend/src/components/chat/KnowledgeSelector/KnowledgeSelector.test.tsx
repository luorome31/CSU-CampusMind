import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { KnowledgeSelector } from './index';
import { chatStore } from '../../../features/chat/chatStore';

describe('KnowledgeSelector', () => {
  const mockKnowledgeBases = [
    { id: 'kb-1', name: 'Course Grades' },
    { id: 'kb-2', name: 'Course Schedule' },
    { id: 'kb-3', name: 'Campus Events' },
  ];

  beforeEach(() => {
    // Reset the store before each test
    chatStore.setState({
      currentKnowledgeIds: [],
      currentDialogId: null,
      messages: [],
      isStreaming: false,
      toolEvents: [],
    });
  });

  it('renders knowledge base chips', () => {
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);
    expect(screen.getByText('Course Grades')).toBeInTheDocument();
    expect(screen.getByText('Course Schedule')).toBeInTheDocument();
    expect(screen.getByText('Campus Events')).toBeInTheDocument();
  });

  it('renders label', () => {
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);
    expect(screen.getByText('知识库')).toBeInTheDocument();
  });

  it('shows clear button when selections exist', () => {
    chatStore.setState({ currentKnowledgeIds: ['kb-1'] });
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);
    expect(screen.getByText('清除')).toBeInTheDocument();
  });

  it('hides clear button when no selections', () => {
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);
    expect(screen.queryByText('清除')).not.toBeInTheDocument();
  });

  it('toggles selection on chip click', async () => {
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);

    const kb1Chip = screen.getByText('Course Grades').closest('button');

    await act(async () => {
      kb1Chip?.click();
    });

    const state = chatStore.getState();
    expect(state.currentKnowledgeIds).toContain('kb-1');
  });

  it('removes selection when already selected chip is clicked', async () => {
    chatStore.setState({ currentKnowledgeIds: ['kb-1'] });
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);

    const kb1Chip = screen.getByText('Course Grades').closest('button');

    await act(async () => {
      kb1Chip?.click();
    });

    const state = chatStore.getState();
    expect(state.currentKnowledgeIds).not.toContain('kb-1');
  });

  it('clears all selections when clear button is clicked', async () => {
    chatStore.setState({ currentKnowledgeIds: ['kb-1', 'kb-2'] });
    render(<KnowledgeSelector knowledgeBases={mockKnowledgeBases} />);

    const clearButton = screen.getByText('清除');

    await act(async () => {
      clearButton.click();
    });

    const state = chatStore.getState();
    expect(state.currentKnowledgeIds).toHaveLength(0);
  });
});
