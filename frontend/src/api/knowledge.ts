import { apiClient } from './client';

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  user_id: string;
  create_time: string;
  update_time: string;
}

export interface KnowledgeFile {
  id: string;
  file_name: string;
  knowledge_id: string;
  user_id: string;
  status: 'process' | 'success' | 'fail' | 'pending_verify' | 'verified' | 'indexing' | 'indexed';
  oss_url: string;
  file_size: number;
  create_time: string;
  update_time: string;
}

class KnowledgeApi {
  async fetchKnowledgeBases(userId: string): Promise<KnowledgeBase[]> {
    return apiClient.get<KnowledgeBase[]>(`/users/${userId}/knowledge`);
  }

  async fetchFiles(knowledgeId: string): Promise<KnowledgeFile[]> {
    return apiClient.get<KnowledgeFile[]>(`/knowledge/${knowledgeId}/files`);
  }

  async fetchFileContent(fileId: string): Promise<string> {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api/v1'}/knowledge_file/${fileId}/content`);
    return response.text();
  }
}

export const knowledgeApi = new KnowledgeApi();
