// mobile/src/features/build/__tests__/buildStore.test.ts
import { useBuildStore } from '../buildStore';

describe('buildStore', () => {
  beforeEach(() => {
    // Reset store state
    useBuildStore.setState({
      activeTab: 'crawl',
      selectedKnowledgeId: null,
      crawlUrls: '',
      tasks: [],
      activeTaskId: null,
      isPolling: false,
      pendingFiles: [],
      pendingReviewCount: 0,
      selectedFile: null,
      fileContent: '',
    });
  });

  describe('setActiveTab', () => {
    it('should update activeTab to review', () => {
      useBuildStore.getState().setActiveTab('review');
      expect(useBuildStore.getState().activeTab).toBe('review');
    });
  });

  describe('setSelectedKnowledgeId', () => {
    it('should update selectedKnowledgeId', () => {
      useBuildStore.getState().setSelectedKnowledgeId('kb-123');
      expect(useBuildStore.getState().selectedKnowledgeId).toBe('kb-123');
    });
  });

  describe('setCrawlUrls', () => {
    it('should update crawlUrls', () => {
      useBuildStore.getState().setCrawlUrls('http://example.com\nhttp://test.com');
      expect(useBuildStore.getState().crawlUrls).toBe('http://example.com\nhttp://test.com');
    });
  });

  describe('clearSelectedFile', () => {
    it('should clear selectedFile and fileContent', () => {
      useBuildStore.setState({
        selectedFile: { id: 'file-1', kb_id: 'kb-1', file_name: 'test.md', status: 'pending_verify', create_time: '', update_time: '' },
        fileContent: '# content',
      });

      useBuildStore.getState().clearSelectedFile();

      expect(useBuildStore.getState().selectedFile).toBeNull();
      expect(useBuildStore.getState().fileContent).toBe('');
    });
  });
});
