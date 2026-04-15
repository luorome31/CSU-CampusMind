/**
 * Crawl API Tests
 */

import { crawlApi } from '../crawl';

// Mock the apiClient
jest.mock('../client', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
  },
}));

import { apiClient } from '../client';

describe('crawlApi', () => {
  beforeEach(() => jest.clearAllMocks());

  describe('submitBatchCrawl', () => {
    it('should return task_id on success', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { task_id: 'task-123' },
      });

      const result = await crawlApi.submitBatchCrawl(['http://example.com'], 'kb-1');

      expect(result).toBe('task-123');
      expect(apiClient.post).toHaveBeenCalledWith('/crawl/batch-with-knowledge', {
        urls: ['http://example.com'],
        knowledge_id: 'kb-1',
      });
    });
  });

  describe('fetchTasks', () => {
    it('should return tasks array', async () => {
      const mockTasks = [{ id: 'task-1', status: 'pending' }];
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { tasks: mockTasks },
      });

      const result = await crawlApi.fetchTasks();

      expect(result).toEqual(mockTasks);
    });

    it('should return empty array if tasks is undefined', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {},
      });

      const result = await crawlApi.fetchTasks();

      expect(result).toEqual([]);
    });
  });

  describe('fetchTaskProgress', () => {
    it('should return task progress', async () => {
      const mockTask = { id: 'task-1', status: 'processing', completed_urls: 5 };
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: mockTask,
      });

      const result = await crawlApi.fetchTaskProgress('task-1');

      expect(result).toEqual(mockTask);
      expect(apiClient.get).toHaveBeenCalledWith('/crawl/tasks/task-1');
    });
  });

  describe('deleteTask', () => {
    it('should call delete endpoint', async () => {
      (apiClient.delete as jest.Mock).mockResolvedValue({ data: {} });

      await crawlApi.deleteTask('task-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/crawl/tasks/task-123');
    });
  });

  describe('retryFailed', () => {
    it('should return task_id object on success', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { task_id: 'task-456' },
      });

      const result = await crawlApi.retryFailed('task-123');

      expect(result).toEqual({ task_id: 'task-456' });
      expect(apiClient.post).toHaveBeenCalledWith('/crawl/tasks/task-123/retry-failed', {});
    });
  });
});