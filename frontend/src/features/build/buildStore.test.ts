import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildStore } from './buildStore';
import { crawlApi } from '../../api/crawl';

vi.mock('../../api/crawl');

describe('buildStore', () => {
  beforeEach(() => {
    // Reset store state
    buildStore.setState({
      activeTab: 'crawl',
      selectedKnowledgeId: null,
      crawlUrls: '',
      tasks: [],
      activeTaskId: null,
      isPolling: false,
      pollingErrorCount: 0,
      isImportModalOpen: false,
      previewUrls: [],
      pendingFiles: [],
      pendingReviewCount: 0,
      selectedFile: null,
      fileContent: '',
      isSaving: false,
      isIndexing: false,
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clear any pending intervals
    const state = buildStore.getState();
    if (state.isPolling) {
      state.stopPolling();
    }
  });

  describe('setActiveTab', () => {
    it('should update activeTab', () => {
      buildStore.getState().setActiveTab('review');
      expect(buildStore.getState().activeTab).toBe('review');
    });
  });

  describe('setSelectedKnowledgeId', () => {
    it('should update selectedKnowledgeId', () => {
      buildStore.getState().setSelectedKnowledgeId('kb_123');
      expect(buildStore.getState().selectedKnowledgeId).toBe('kb_123');
    });
  });

  describe('setCrawlUrls', () => {
    it('should update crawlUrls', () => {
      buildStore.getState().setCrawlUrls('http://example.com\nhttp://test.com');
      expect(buildStore.getState().crawlUrls).toBe('http://example.com\nhttp://test.com');
    });
  });

  describe('modal controls', () => {
    it('should open import modal', () => {
      buildStore.getState().openImportModal();
      expect(buildStore.getState().isImportModalOpen).toBe(true);
    });

    it('should close import modal and clear previewUrls', () => {
      buildStore.setState({ isImportModalOpen: true, previewUrls: ['http://a.com'] });
      buildStore.getState().closeImportModal();
      expect(buildStore.getState().isImportModalOpen).toBe(false);
      expect(buildStore.getState().previewUrls).toEqual([]);
    });
  });

  describe('setPreviewUrls', () => {
    it('should update previewUrls', () => {
      buildStore.getState().setPreviewUrls(['http://a.com', 'http://b.com']);
      expect(buildStore.getState().previewUrls).toEqual(['http://a.com', 'http://b.com']);
    });
  });

  describe('submitBatchCrawl', () => {
    it('should return null if no knowledge selected', async () => {
      const result = await buildStore.getState().submitBatchCrawl(['http://a.com']);
      expect(result).toBeNull();
    });

    it('should return null if urls empty', async () => {
      buildStore.setState({ selectedKnowledgeId: 'kb_1' });
      const result = await buildStore.getState().submitBatchCrawl([]);
      expect(result).toBeNull();
    });

    it('should submit crawl and return task id', async () => {
      buildStore.setState({ selectedKnowledgeId: 'kb_1' });
      vi.mocked(crawlApi.submitBatchCrawl).mockResolvedValue('task_new');
      vi.mocked(crawlApi.fetchTasks).mockResolvedValue([]);

      const result = await buildStore.getState().submitBatchCrawl(['http://a.com']);

      expect(result).toBe('task_new');
      expect(crawlApi.submitBatchCrawl).toHaveBeenCalledWith(
        ['http://a.com'],
        'kb_1'
      );
    });
  });

  describe('stopPolling', () => {
    it('should set isPolling to false', () => {
      buildStore.setState({ isPolling: true, pollingErrorCount: 5 });
      buildStore.getState().stopPolling();
      expect(buildStore.getState().isPolling).toBe(false);
      expect(buildStore.getState().pollingErrorCount).toBe(0);
    });
  });

  describe('clearSelectedFile', () => {
    it('should clear selected file and content', () => {
      buildStore.setState({
        selectedFile: { id: 'f1', file_name: 'test.md', knowledge_id: 'kb1', user_id: 'u1', status: 'pending_verify', oss_url: '', file_size: 100, create_time: '', update_time: '' },
        fileContent: '# content'
      });
      buildStore.getState().clearSelectedFile();
      expect(buildStore.getState().selectedFile).toBeNull();
      expect(buildStore.getState().fileContent).toBe('');
    });
  });
});
