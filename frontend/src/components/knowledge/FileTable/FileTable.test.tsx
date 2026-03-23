import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FileTable } from './FileTable';
import type { KnowledgeFile } from '../../../api/knowledge';

describe('FileTable', () => {
  const mockFiles: KnowledgeFile[] = [
    { id: 'f1', file_name: 'doc.md', knowledge_id: 'kb1', user_id: 'u1', status: 'success', oss_url: '', file_size: 1024, create_time: '2024-01-01', update_time: '2024-01-02' },
    { id: 'f2', file_name: 'notes.md', knowledge_id: 'kb1', user_id: 'u1', status: 'process', oss_url: '', file_size: 2048, create_time: '2024-01-01', update_time: '2024-01-03' },
  ];

  it('renders file rows', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('doc.md')).toBeInTheDocument();
    expect(screen.getByText('notes.md')).toBeInTheDocument();
  });

  it('renders status badges', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('成功')).toBeInTheDocument();
    expect(screen.getByText('处理中')).toBeInTheDocument();
  });

  it('calls onFileClick when row clicked', () => {
    const handleClick = vi.fn();
    render(<FileTable files={mockFiles} onFileClick={handleClick} />);
    screen.getByText('doc.md').click();
    expect(handleClick).toHaveBeenCalledWith(mockFiles[0]);
  });

  it('formats file size correctly', () => {
    render(<FileTable files={mockFiles} onFileClick={() => {}} />);
    expect(screen.getByText('1.0 KB')).toBeInTheDocument();
    expect(screen.getByText('2.0 KB')).toBeInTheDocument();
  });
});
