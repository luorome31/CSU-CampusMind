// mobile/src/api/dialog.ts
import { apiClient } from './client';

export interface Dialog {
  id: string;
  title?: string;
  updated_at: string;
}

export async function listDialogs(limit = 50): Promise<Dialog[]> {
  const response = await apiClient.get<Dialog[]>(`/dialogs?limit=${limit}`);
  return response.data;
}

export async function deleteDialog(dialogId: string): Promise<void> {
  await apiClient.delete(`/dialogs/${dialogId}`);
}
