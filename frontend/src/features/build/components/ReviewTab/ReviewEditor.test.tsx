import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReviewEditor } from './ReviewEditor';
import { buildStore } from '../../buildStore';

const mockFile = {
  id: 'file_1',
  file_name: 'test.md',
  knowledge_id: 'kb_1',
  user_id: 'user_1',
  status: 'pending_verify' as const,
  oss_url: 'https://oss.example.com/test.md',
  file_size: 1024,
  create_time: '2024-01-01T12:00:00',
  update_time: '2024-01-01T12:00:00',
};

describe('ReviewEditor', () => {
  beforeEach(() => {
    buildStore.setState({
      selectedFile: null,
      fileContent: '',
      isSaving: false,
      isIndexing: false,
    });
  });

  it('should render empty state when no file selected', () => {
    render(<ReviewEditor />);
    expect(screen.getByText(/请从左侧选择文件/)).toBeInTheDocument();
  });

  it('should render file name when file selected', () => {
    buildStore.setState({
      selectedFile: mockFile,
      fileContent: '# Test Content',
    });
    render(<ReviewEditor />);
    expect(screen.getByText(/test\.md/)).toBeInTheDocument();
  });

  it('should render action buttons when file selected', () => {
    buildStore.setState({
      selectedFile: mockFile,
      fileContent: '# Test Content',
    });
    render(<ReviewEditor />);
    expect(screen.getByRole('button', { name: /保存/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /确认索引/ })).toBeInTheDocument();
  });
});
