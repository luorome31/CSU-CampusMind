import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { KnowledgeCard } from '../KnowledgeCard';

describe('KnowledgeCard', () => {
  const mockKB = {
    id: '1',
    name: '测试知识库',
    description: '这是一个测试知识库',
    file_count: 5,
  };

  it('should render KB name and description', () => {
    const { getByText } = render(
      <KnowledgeCard
        knowledge={mockKB}
        fileCount={mockKB.file_count}
        onClick={() => {}}
      />
    );
    expect(getByText('测试知识库')).toBeTruthy();
    expect(getByText('这是一个测试知识库')).toBeTruthy();
    expect(getByText('5 个文件')).toBeTruthy();
  });

  it('should call onClick when pressed', () => {
    const onClick = jest.fn();
    const { getByText } = render(
      <KnowledgeCard
        knowledge={mockKB}
        fileCount={mockKB.file_count}
        onClick={onClick}
      />
    );
    fireEvent.press(getByText('测试知识库'));
    expect(onClick).toHaveBeenCalled();
  });
});