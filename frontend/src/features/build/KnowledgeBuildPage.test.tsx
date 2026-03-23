import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeBuildPage } from './KnowledgeBuildPage';

const mockSetActiveTab = vi.fn((tab) => {
  mockState = createMockState({ activeTab: tab });
});
const mockFetchPendingFiles = vi.fn();
const mockFetchTasks = vi.fn();

const createMockState = (overrides = {}) => ({
  activeTab: 'crawl' as const,
  pendingReviewCount: 0,
  tasks: [],
  pendingFiles: [],
  selectedFile: null,
  fileContent: '',
  isPolling: false,
  crawlUrls: '',
  selectedKnowledgeId: null,
  isImportModalOpen: false,
  previewUrls: [],
  isSaving: false,
  isIndexing: false,
  setActiveTab: mockSetActiveTab,
  fetchPendingFiles: mockFetchPendingFiles,
  fetchTasks: mockFetchTasks,
  ...overrides,
});

let mockState = createMockState();

vi.mock('./buildStore', () => ({
  buildStore: vi.fn((selector) => {
    if (selector) {
      return selector(mockState);
    }
    return mockState;
  }),
}));

describe('KnowledgeBuildPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState = createMockState();
  });

  it('should render two tabs', () => {
    render(<KnowledgeBuildPage />);
    expect(screen.getByRole('tab', { name: /爬取任务/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /审核队列/ })).toBeInTheDocument();
  });

  it('should render page title', () => {
    render(<KnowledgeBuildPage />);
    expect(screen.getByText(/知识库构建/)).toBeInTheDocument();
  });
});
