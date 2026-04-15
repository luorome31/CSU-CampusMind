import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { FileTable } from '../FileTable';
import type { KnowledgeFile } from '../../../../api/knowledge';

describe('FileTable', () => {
  const mockFiles: KnowledgeFile[] = [
    {
      id: '1',
      kb_id: 'kb1',
      file_name: '测试文件.pdf',
      status: 'ready',
      create_time: '2024-01-01T00:00:00Z',
      update_time: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      kb_id: 'kb1',
      file_name: '处理中文件.pdf',
      status: 'processing',
      create_time: '2024-01-02T00:00:00Z',
      update_time: '2024-01-02T00:00:00Z',
    },
  ];

  it('should render empty state when no files', () => {
    const { getByText } = render(
      <FileTable files={[]} onFileClick={() => {}} />
    );
    expect(getByText('暂无文件')).toBeTruthy();
  });

  it('should render file list', () => {
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={() => {}} />
    );
    expect(getByText('测试文件.pdf')).toBeTruthy();
    expect(getByText('处理中文件.pdf')).toBeTruthy();
  });

  it('should render status badges', () => {
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={() => {}} />
    );
    expect(getByText('就绪')).toBeTruthy();
    expect(getByText('处理中')).toBeTruthy();
  });

  it('should call onFileClick when file pressed', () => {
    const onFileClick = jest.fn();
    const { getByText } = render(
      <FileTable files={mockFiles} onFileClick={onFileClick} />
    );
    fireEvent.press(getByText('测试文件.pdf'));
    expect(onFileClick).toHaveBeenCalledWith(mockFiles[0]);
  });
});
