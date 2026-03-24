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

interface BatchCrawlResponse {
  task_id: string;
  status: string;
  message: string;
}

class CrawlApi {
  async submitBatchCrawl(urls: string[], knowledgeId: string): Promise<string> {
    const response = await apiClient.post<BatchCrawlResponse>('/crawl/batch-with-knowledge', {
      urls,
      knowledge_id: knowledgeId,
    });
    return response.task_id;
  }

  async fetchTasks(): Promise<CrawlTask[]> {
    return apiClient.get<CrawlTask[]>('/crawl/tasks');
  }

  async fetchTaskProgress(taskId: string): Promise<CrawlTask> {
    return apiClient.get<CrawlTask>(`/crawl/tasks/${taskId}`);
  }

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/crawl/tasks/${taskId}`);
  }

  async retryFailed(taskId: string): Promise<{ task_id: string; retry_count: number }> {
    return apiClient.post(`/crawl/tasks/${taskId}/retry-failed`, {});
  }
}

export const crawlApi = new CrawlApi();
