import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { RAGSwitch } from '../RAGSwitch';
import type { KnowledgeBase } from '../../../../api/knowledge';

describe('RAGSwitch', () => {
  const mockKBs: KnowledgeBase[] = [
    { id: '1', name: 'KB1', description: '', user_id: 'u1', create_time: '', update_time: '', file_count: 3 },
    { id: '2', name: 'KB2', description: '', user_id: 'u1', create_time: '', update_time: '', file_count: 5 },
  ];

  it('should render RAG toggle', () => {
    const { getByText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={() => {}}
        onSelect={() => {}}
      />
    );
    expect(getByText('RAG 检索')).toBeTruthy();
  });

  it('should render knowledge bases', () => {
    const { getByText, getByLabelText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={() => {}}
        onSelect={() => {}}
      />
    );
    // Expand the list first
    fireEvent(getByLabelText('展开知识库列表'), 'press');
    expect(getByText('KB1')).toBeTruthy();
    expect(getByText('KB2')).toBeTruthy();
  });

  it('should call onToggle when switch pressed', () => {
    const onToggle = jest.fn();
    const { getByText } = render(
      <RAGSwitch
        enabled={true}
        selectedIds={[]}
        knowledgeBases={mockKBs}
        onToggle={onToggle}
        onSelect={() => {}}
      />
    );
    fireEvent(getByText('RAG 检索'), 'press');
    expect(onToggle).toHaveBeenCalled();
  });
});