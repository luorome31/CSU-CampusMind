import React from 'react';
import { render } from '@testing-library/react-native';
import { CrawlPanel } from '../CrawlPanel';

// Mock the build store
jest.mock('../../../../features/build/buildStore', () => ({
  useBuildStore: jest.fn((selector) => {
    if (typeof selector === 'function') {
      return selector({
        crawlUrls: '',
        setCrawlUrls: jest.fn(),
        submitBatchCrawl: jest.fn(),
        isPolling: false,
      });
    }
    return jest.fn();
  }),
}));

const mockKnowledgeBases = [
  { id: 'kb-1', name: '知识库1', file_count: 10 },
  { id: 'kb-2', name: '知识库2', file_count: 5 },
];

describe('CrawlPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render knowledge base chips', () => {
    const { getByText } = render(
      <CrawlPanel
        knowledgeBases={mockKnowledgeBases}
        onSelectKnowledge={jest.fn()}
        selectedKnowledgeId={null}
        onOpenImportModal={jest.fn()}
      />
    );

    expect(getByText('知识库1')).toBeTruthy();
    expect(getByText('知识库2')).toBeTruthy();
  });

  it('should render URL textarea', () => {
    const { getByPlaceholderText } = render(
      <CrawlPanel
        knowledgeBases={mockKnowledgeBases}
        onSelectKnowledge={jest.fn()}
        selectedKnowledgeId={null}
        onOpenImportModal={jest.fn()}
      />
    );

    expect(getByPlaceholderText('输入URL，每行一个')).toBeTruthy();
  });

  it('should render action buttons', () => {
    const { getByText } = render(
      <CrawlPanel
        knowledgeBases={mockKnowledgeBases}
        onSelectKnowledge={jest.fn()}
        selectedKnowledgeId={null}
        onOpenImportModal={jest.fn()}
      />
    );

    expect(getByText('开始爬取')).toBeTruthy();
    expect(getByText('批量导入')).toBeTruthy();
    expect(getByText('清空')).toBeTruthy();
  });

  it('should show file count when knowledge base is selected', () => {
    const { getByText } = render(
      <CrawlPanel
        knowledgeBases={mockKnowledgeBases}
        onSelectKnowledge={jest.fn()}
        selectedKnowledgeId="kb-1"
        onOpenImportModal={jest.fn()}
      />
    );

    expect(getByText('10 个文件')).toBeTruthy();
  });
});
