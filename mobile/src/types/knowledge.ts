/**
 * Knowledge 模块类型定义
 */

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  file_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeFile {
  id: string;
  kb_id: string;
  name: string;
  status: 'pending' | 'processing' | 'ready' | 'error';
  size?: number;
  created_at: string;
  updated_at: string;
}

export interface CrawlTask {
  id: string;
  url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewItem {
  id: string;
  task_id: string;
  content: string;
  original_url?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}
