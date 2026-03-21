// src/api/dialog.ts
import { apiClient } from './client';
import type { ChatMessage, ToolEvent } from '../features/chat/chatStore';

export interface Dialog {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatHistoryResponse {
  id: string;
  dialog_id: string;
  role: string;
  content: string;
  events: ToolEvent[];
  created_at: string;
}

/**
 * Get dialog history messages.
 */
export async function getDialogHistory(dialogId: string): Promise<ChatMessage[]> {
  const history = await apiClient.get<ChatHistoryResponse[]>(
    `/dialogs/${dialogId}/history`
  );

  return history.map((item) => ({
    id: item.id,
    role: item.role as 'user' | 'assistant',
    content: item.content,
    events: item.events || [],
    createdAt: new Date(item.created_at),
  }));
}

/**
 * Get all user dialogs.
 */
export async function getUserDialogs(userId: string): Promise<Dialog[]> {
  return apiClient.get<Dialog[]>(`/users/${userId}/dialogs`);
}
