// src/api/dialog.ts
import { apiClient } from './client';

export interface Dialog {
  id: string;
  user_id?: string;
  agent_id?: string;
  title?: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  file_url?: string;
  events?: string;
  created_at: string;
}

export async function listDialogs(limit = 50): Promise<Dialog[]> {
  return apiClient.get<Dialog[]>(`/dialogs?limit=${limit}`);
}

export async function getDialogMessages(dialogId: string): Promise<ChatMessage[]> {
  return apiClient.get<ChatMessage[]>(`/dialogs/${dialogId}/messages`);
}

export async function deleteDialog(dialogId: string): Promise<void> {
  return apiClient.delete<void>(`/dialogs/${dialogId}`);
}

export async function updateDialogTitle(dialogId: string, title: string): Promise<Dialog> {
  return apiClient.patch<Dialog>(`/dialogs/${dialogId}`, { title });
}
