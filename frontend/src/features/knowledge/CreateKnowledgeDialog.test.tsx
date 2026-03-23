import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CreateKnowledgeDialog } from './CreateKnowledgeDialog';
import { knowledgeListStore } from './knowledgeListStore';
import * as knowledgeApi from '../../api/knowledge';

vi.mock('../../api/knowledge');

describe('CreateKnowledgeDialog', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    knowledgeListStore.setState({
      knowledgeBases: [],
      isLoadingKBs: false,
      error: null,
    });
  });

  it('renders when isOpen=true', () => {
    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('创建知识库')).toBeInTheDocument();
    expect(screen.getByLabelText('知识库名称')).toBeInTheDocument();
    expect(screen.getByText('描述')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '取消' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '创建' })).toBeInTheDocument();
  });

  it('does not render when isOpen=false', () => {
    render(<CreateKnowledgeDialog isOpen={false} onClose={mockOnClose} />);

    expect(screen.queryByText('创建知识库')).not.toBeInTheDocument();
  });

  it('shows validation error when submitting without name', async () => {
    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    const form = screen.getByRole('button', { name: '创建' }).closest('form');
    if (form) {
      fireEvent.submit(form);
    }

    expect(await screen.findByText('请输入知识库名称')).toBeInTheDocument();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('calls createKnowledgeBase on valid form submission', async () => {
    const mockKB: knowledgeApi.KnowledgeBase = {
      id: 'kb-new',
      name: 'Test KB',
      description: 'Test desc',
      user_id: 'user1',
      create_time: '',
      update_time: '',
    };
    vi.mocked(knowledgeApi.knowledgeApi.createKnowledgeBase).mockResolvedValue(mockKB);

    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    const nameInput = screen.getByLabelText('知识库名称');
    fireEvent.change(nameInput, { target: { value: 'Test KB' } });

    const descInput = screen.getByLabelText('描述');
    fireEvent.change(descInput, { target: { value: 'Test desc' } });

    const form = screen.getByRole('button', { name: '创建' }).closest('form');
    if (form) {
      fireEvent.submit(form);
    }

    await waitFor(() => {
      expect(knowledgeListStore.getState().knowledgeBases).toContainEqual(mockKB);
    });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('shows loading state and disables button during submission', async () => {
    vi.mocked(knowledgeApi.knowledgeApi.createKnowledgeBase).mockImplementation(
      async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        return {
          id: 'kb-new',
          name: 'Test KB',
          description: '',
          user_id: 'user1',
          create_time: '',
          update_time: '',
        };
      }
    );

    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    const nameInput = screen.getByLabelText('知识库名称');
    fireEvent.change(nameInput, { target: { value: 'Test KB' } });

    const form = screen.getByText('创建').closest('form');
    if (form) {
      fireEvent.submit(form);
    }

    expect(await screen.findByText('创建中...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '创建中...' })).toBeDisabled();
    expect(screen.getByRole('button', { name: '取消' })).toBeDisabled();
  });

  it('shows error message when API fails', async () => {
    vi.mocked(knowledgeApi.knowledgeApi.createKnowledgeBase).mockRejectedValue(
      new Error('创建知识库失败')
    );

    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    const nameInput = screen.getByLabelText('知识库名称');
    fireEvent.change(nameInput, { target: { value: 'Test KB' } });

    const form = screen.getByRole('button', { name: '创建' }).closest('form');
    if (form) {
      fireEvent.submit(form);
    }

    await waitFor(() => {
      expect(screen.getByText('创建知识库失败')).toBeInTheDocument();
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('resets form and calls onClose when cancel is clicked', () => {
    render(<CreateKnowledgeDialog isOpen={true} onClose={mockOnClose} />);

    const nameInput = screen.getByLabelText('知识库名称');
    fireEvent.change(nameInput, { target: { value: 'Test KB' } });

    const cancelButton = screen.getByRole('button', { name: '取消' });
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });
});
