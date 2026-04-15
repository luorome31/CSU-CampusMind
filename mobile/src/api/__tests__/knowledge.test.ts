import { knowledgeApi, KnowledgeFile } from '../knowledge';

jest.mock('../client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
  },
}));

import { apiClient } from '../client';

describe('knowledgeApi', () => {
  beforeEach(() => jest.clearAllMocks());

  describe('getPendingFiles', () => {
    it('should return pending files array', async () => {
      const mockFiles: KnowledgeFile[] = [
        {
          id: 'file-1',
          kb_id: 'kb-1',
          file_name: 'test.md',
          status: 'pending_verify',
          create_time: '2024-01-01T00:00:00Z',
          update_time: '2024-01-01T00:00:00Z',
        },
      ];
      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockFiles });

      const result = await knowledgeApi.getPendingFiles();

      expect(result).toEqual(mockFiles);
      expect(apiClient.get).toHaveBeenCalledWith('/knowledge_file/pending_verify');
    });

    it('should return empty array when no data', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: null });

      const result = await knowledgeApi.getPendingFiles();

      expect(result).toEqual([]);
    });
  });

  describe('getFileContent', () => {
    it('should return file content string', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: '# Hello World' });

      const result = await knowledgeApi.getFileContent('file-123');

      expect(result).toBe('# Hello World');
      expect(apiClient.get).toHaveBeenCalledWith('/knowledge_file/file-123/content');
    });
  });

  describe('updateFileContent', () => {
    it('should call put with content', async () => {
      (apiClient.put as jest.Mock).mockResolvedValue({ data: {} });

      await knowledgeApi.updateFileContent('file-123', '# Updated content');

      expect(apiClient.put).toHaveBeenCalledWith('/knowledge_file/file-123/content', {
        content: '# Updated content',
      });
    });
  });

  describe('triggerIndex', () => {
    it('should call trigger_index endpoint with enable_vector and enable_keyword', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ data: {} });

      await knowledgeApi.triggerIndex('file-123');

      expect(apiClient.post).toHaveBeenCalledWith('/knowledge_file/file-123/trigger_index', {
        enable_vector: true,
        enable_keyword: true,
      });
    });
  });
});