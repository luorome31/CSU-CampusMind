import { describe, it, expect, vi, beforeEach } from 'vitest';
import { crawlApi, CrawlTask } from '../api/crawl';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('crawlApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
    });
  });

  describe('submitBatchCrawl', () => {
    it('should call POST /api/v1/crawl/batch-with-knowledge with correct body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ task_id: 'task_123', status: 'processing' }),
        text: () => Promise.resolve('{"task_id":"task_123","status":"processing"}'),
      });

      const result = await crawlApi.submitBatchCrawl(
        ['http://example.com'],
        'kb_abc'
      );

      expect(result).toBe('task_123');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/crawl/batch-with-knowledge'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ urls: ['http://example.com'], knowledge_id: 'kb_abc' }),
        })
      );
    });
  });

  describe('fetchTasks', () => {
    it('should return array of tasks', async () => {
      const mockTasks: CrawlTask[] = [{
        id: 'task_1',
        knowledge_id: 'kb_1',
        user_id: 'user_1',
        total_urls: 10,
        completed_urls: 5,
        success_count: 4,
        fail_count: 1,
        status: 'processing',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:01:00',
      }];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTasks),
        text: () => Promise.resolve(JSON.stringify(mockTasks)),
      });

      const result = await crawlApi.fetchTasks();
      expect(result).toEqual(mockTasks);
    });
  });

  describe('fetchTaskProgress', () => {
    it('should return task progress for given task_id', async () => {
      const mockTask: CrawlTask = {
        id: 'task_xyz',
        knowledge_id: 'kb_abc',
        user_id: 'user_1',
        total_urls: 10,
        completed_urls: 10,
        success_count: 9,
        fail_count: 1,
        status: 'SUCCESS',
        create_time: '2024-01-01T00:00:00',
        update_time: '2024-01-01T00:02:00',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTask),
        text: () => Promise.resolve(JSON.stringify(mockTask)),
      });

      const result = await crawlApi.fetchTaskProgress('task_xyz');
      expect(result).toEqual(mockTask);
    });
  });
});
