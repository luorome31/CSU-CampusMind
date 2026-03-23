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
  async fetchKnowledgeBases(): Promise<KnowledgeBase[]> {
    return apiClient.get<KnowledgeBase[]>(`/knowledge`);
  }

  async fetchFiles(knowledgeId: string): Promise<KnowledgeFile[]> {
    return apiClient.get<KnowledgeFile[]>(`/knowledge/${knowledgeId}/files`);
  }

  async fetchFileContent(fileId: string): Promise<string> {
    const token = sessionStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const response = await fetch(`${baseUrl}/knowledge_file/${fileId}/content`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch content: ${response.status}`);
    }
    return response.text();
  }

  async createKnowledgeBase(name: string, description?: string): Promise<KnowledgeBase> {
    return apiClient.post<KnowledgeBase>(`/knowledge/create`, { name, description });
  }
}

export const knowledgeApi = new KnowledgeApi();
