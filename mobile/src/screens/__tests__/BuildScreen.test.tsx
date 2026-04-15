// mobile/src/screens/__tests__/BuildScreen.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { BuildScreen } from '../BuildScreen';
import { useBuildStore } from '../../features/build/buildStore';

// Mock the build store
jest.mock('../../features/build/buildStore', () => ({
  useBuildStore: jest.fn(),
}));

const mockUseBuildStore = useBuildStore as jest.MockedFunction<typeof useBuildStore>;

// Mock sub-components
jest.mock('../../components/build/SegmentedControl', () => ({
  SegmentedControl: ({ options, value, onChange }: any) => {
    const { View, Text, Pressable } = require('react-native');
    return (
      <View testID="segmented-control">
        {options.map((opt: any) => (
          <Pressable key={opt.value} onPress={() => onChange(opt.value)}>
            <Text>{opt.label} {opt.value === value ? '(active)' : ''}</Text>
          </Pressable>
        ))}
      </View>
    );
  },
}));

jest.mock('../../components/build/CrawlTab/CrawlPanel', () => ({
  CrawlPanel: ({ knowledgeBases }: any) => {
    const { View, Text } = require('react-native');
    return (
      <View testID="crawl-panel">
        <Text>CrawlPanel</Text>
        <Text>KB Count: {knowledgeBases.length}</Text>
      </View>
    );
  },
}));

jest.mock('../../components/build/CrawlTab/TaskList', () => ({
  TaskList: () => {
    const { View, Text } = require('react-native');
    return (
      <View testID="task-list">
        <Text>TaskList</Text>
      </View>
    );
  },
}));

jest.mock('../../components/build/CrawlTab/UrlImportModal', () => ({
  UrlImportModal: () => {
    const { View, Text } = require('react-native');
    return (
      <View testID="url-import-modal">
        <Text>UrlImportModal</Text>
      </View>
    );
  },
}));

jest.mock('../../components/build/ReviewTab/ReviewInbox', () => ({
  ReviewInbox: ({ count, onPress }: any) => {
    const { View, Text, Pressable } = require('react-native');
    return (
      <Pressable testID="review-inbox" onPress={onPress}>
        <Text>ReviewInbox (count: {count})</Text>
      </Pressable>
    );
  },
}));

jest.mock('../../components/build/ReviewTab/ReviewEditor', () => ({
  ReviewEditor: () => {
    const { View, Text } = require('react-native');
    return (
      <View testID="review-editor">
        <Text>ReviewEditor</Text>
      </View>
    );
  },
}));

jest.mock('../../components/build/ReviewTab/FileSelectModal', () => ({
  FileSelectModal: ({ visible, files, onSelect, onClose }: any) => {
    const { View, Text, Pressable } = require('react-native');
    if (!visible) return null;
    return (
      <View testID="file-select-modal">
        <Text>FileSelectModal (files: {files.length})</Text>
        <Pressable onPress={onClose}><Text>Close</Text></Pressable>
      </View>
    );
  },
}));

// Mock lucide icons
jest.mock('lucide-react-native', () => ({
  ChevronLeft: () => 'ChevronLeft',
}));

// Mock safe area context
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => {
    const { View } = require('react-native');
    return <View>{children}</View>;
  },
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

// Mock navigation
const mockGoBack = jest.fn();
const mockNavigation = {
  goBack: mockGoBack,
} as any;

const mockRoute = {} as any;

const mockPendingFiles = [
  { id: 'file-1', kb_id: 'kb-1', file_name: 'test1.pdf', status: 'pending' as const, create_time: '2024-01-01', update_time: '2024-01-01' },
  { id: 'file-2', kb_id: 'kb-1', file_name: 'test2.pdf', status: 'pending' as const, create_time: '2024-01-02', update_time: '2024-01-02' },
];

// Helper to create mock store state
const createMockState = (overrides: any = {}) => ({
  activeTab: 'crawl',
  setActiveTab: jest.fn(),
  selectedKnowledgeId: null,
  setSelectedKnowledgeId: jest.fn(),
  fetchTasks: jest.fn().mockResolvedValue(undefined),
  fetchPendingFiles: jest.fn().mockResolvedValue(undefined),
  fetchFileContent: jest.fn().mockResolvedValue(undefined),
  pendingFiles: mockPendingFiles,
  pendingReviewCount: 2,
  openImportModal: jest.fn(),
  crawlUrls: '',
  tasks: [],
  activeTaskId: null,
  isPolling: false,
  pollingErrorCount: 0,
  isImportModalOpen: false,
  previewUrls: [],
  selectedFile: null,
  fileContent: '',
  isLoadingContent: false,
  isSaving: false,
  isIndexing: false,
  isPreview: false,
  closeImportModal: jest.fn(),
  setPreviewUrls: jest.fn(),
  submitBatchCrawl: jest.fn(),
  startPolling: jest.fn(),
  stopPolling: jest.fn(),
  removeTask: jest.fn(),
  retryFailedUrls: jest.fn(),
  clearCompletedTasks: jest.fn(),
  updateFileContent: jest.fn(),
  triggerIndex: jest.fn(),
  clearSelectedFile: jest.fn(),
  setIsPreview: jest.fn(),
  ...overrides,
});

describe('BuildScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState());
      }
      return jest.fn();
    });
  });

  it('should render header with back button and segmented control', () => {
    const { getByTestId, getByText } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    expect(getByTestId('segmented-control')).toBeTruthy();
    expect(getByText(/爬取任务/)).toBeTruthy();
    expect(getByText(/审核队列/)).toBeTruthy();
  });

  it('should render crawl tab content by default', () => {
    const { getByTestId, getByText } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    expect(getByTestId('crawl-panel')).toBeTruthy();
    expect(getByTestId('task-list')).toBeTruthy();
    expect(getByText('CrawlPanel')).toBeTruthy();
    expect(getByText('TaskList')).toBeTruthy();
  });

  it('should switch to review tab when segment is tapped', () => {
    const mockSetActiveTab = jest.fn();
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({ setActiveTab: mockSetActiveTab }));
      }
      return jest.fn();
    });

    const { getByText } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    fireEvent.press(getByText('审核队列'));
    expect(mockSetActiveTab).toHaveBeenCalledWith('review');
  });

  it('should render review tab content when activeTab is review', () => {
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({ activeTab: 'review' }));
      }
      return jest.fn();
    });

    const { getByTestId, getByText } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    expect(getByTestId('review-inbox')).toBeTruthy();
    expect(getByTestId('review-editor')).toBeTruthy();
    expect(getByText('ReviewInbox (count: 2)')).toBeTruthy();
    expect(getByText('ReviewEditor')).toBeTruthy();
  });

  it('should show FileSelectModal when ReviewInbox is pressed', () => {
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({ activeTab: 'review' }));
      }
      return jest.fn();
    });

    const { getByTestId, queryByTestId } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    // Modal should not be visible initially
    expect(queryByTestId('file-select-modal')).toBeNull();

    // Press the review inbox
    fireEvent.press(getByTestId('review-inbox'));

    // Modal should now be visible
    expect(getByTestId('file-select-modal')).toBeTruthy();
  });

  it('should render UrlImportModal', () => {
    const { getByTestId } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    expect(getByTestId('url-import-modal')).toBeTruthy();
  });

  it('should call fetchTasks and fetchPendingFiles on mount', () => {
    const mockFetchTasks = jest.fn().mockResolvedValue(undefined);
    const mockFetchPendingFiles = jest.fn().mockResolvedValue(undefined);

    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({
          fetchTasks: mockFetchTasks,
          fetchPendingFiles: mockFetchPendingFiles,
        }));
      }
      return jest.fn();
    });

    render(<BuildScreen navigation={mockNavigation} route={mockRoute} />);

    expect(mockFetchTasks).toHaveBeenCalled();
    expect(mockFetchPendingFiles).toHaveBeenCalled();
  });

  it('should auto-select first file when switching to review tab with pending files', () => {
    const mockFetchFileContent = jest.fn().mockResolvedValue(undefined);

    // Start with crawl tab
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({
          activeTab: 'crawl',
          fetchFileContent: mockFetchFileContent,
        }));
      }
      return jest.fn();
    });

    const { rerender } = render(
      <BuildScreen navigation={mockNavigation} route={mockRoute} />
    );

    // Simulate tab change to review
    mockUseBuildStore.mockImplementation((selector: any) => {
      if (typeof selector === 'function') {
        return selector(createMockState({
          activeTab: 'review',
          fetchFileContent: mockFetchFileContent,
          pendingFiles: mockPendingFiles,
        }));
      }
      return jest.fn();
    });

    rerender(<BuildScreen navigation={mockNavigation} route={mockRoute} />);

    expect(mockFetchFileContent).toHaveBeenCalledWith('file-1');
  });
});
