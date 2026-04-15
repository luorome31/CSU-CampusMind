/**
 * Crawl API Client
 */

import { apiClient } from './client';

export interface FailedUrl {
  url: string;
  error: string;
  timestamp: string;
}

export interface CrawlTask {
  id: string;
  knowledge_id: string;
  user_id: string;
  total_urls: number;
  completed_urls: number;
  success_count: number;
  fail_count: number;
  status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed' | 'failed';
  failed_urls?: FailedUrl[];
  create_time: string;
  update_time: string;
}

export const crawlApi = {
  async submitBatchCrawl(urls: string[], knowledgeId: string): Promise<string> {
    const response = await apiClient.post<{ task_id: string }>('/crawl/batch-with-knowledge', {
      urls,
      knowledge_id: knowledgeId,
    });
    return response.data.task_id;
  },

  async fetchTasks(): Promise<CrawlTask[]> {
    const response = await apiClient.get<{ tasks: CrawlTask[] }>('/crawl/tasks');
    return response.data.tasks || [];
  },

  async fetchTaskProgress(taskId: string): Promise<CrawlTask> {
    const response = await apiClient.get<CrawlTask>(`/crawl/tasks/${taskId}`);
    return response.data;
  },

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/crawl/tasks/${taskId}`);
  },

  async retryFailed(taskId: string): Promise<{ task_id: string }> {
    const response = await apiClient.post(`/crawl/tasks/${taskId}/retry-failed`, {});
    return response.data;
  },
};