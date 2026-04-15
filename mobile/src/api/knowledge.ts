// mobile/src/api/knowledge.ts
import { apiClient } from './client';

export interface KnowledgeFile {
  id: string;
  kb_id: string;
  file_name: string;
  status: 'pending' | 'processing' | 'ready' | 'error' | 'verified';
  size?: number;
  create_time: string;
  update_time: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  user_id: string;
  create_time: string;
  update_time: string;
  file_count: number;
}

export const knowledgeApi = {
  async fetchKnowledgeBases(): Promise<KnowledgeBase[]> {
    const response = await apiClient.get<KnowledgeBase[]>('/knowledge');
    return response.data || [];
  },

  async getPendingFiles(): Promise<KnowledgeFile[]> {
    const response = await apiClient.get<KnowledgeFile[]>('/knowledge_file/pending_verify');
    return response.data || [];
  },

  async getFileContent(fileId: string): Promise<string> {
    const response = await apiClient.get(`/knowledge_file/${fileId}/content`);
    return response.data;
  },

  async updateFileContent(fileId: string, content: string): Promise<void> {
    await apiClient.put(`/knowledge_file/${fileId}/content`, { content });
  },

  async triggerIndex(fileId: string): Promise<void> {
    await apiClient.post(`/knowledge_file/${fileId}/trigger_index`, {
      enable_vector: true,
      enable_keyword: true,
    });
  },
};