import { apiClient } from '../../../api/client';

export interface CrawlTask {
  id: string;
  knowledge_id: string;
  user_id: string;
  total_urls: number;
  completed_urls: number;
  success_count: number;
  fail_count: number;
  status: 'pending' | 'processing' | 'SUCCESS' | 'FAILED' | 'completed';
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
}

export const crawlApi = new CrawlApi();
