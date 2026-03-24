import { apiClient } from '../../../api/client';
import { User, Session, UpdateProfileData } from '../types';

export const profileApi = {
  getProfile: () =>
    apiClient.get<User>('/users/me'),

  updateProfile: (data: UpdateProfileData) =>
    apiClient.patch<User>('/users/me', data),

  getSessions: () =>
    apiClient.get<Session[]>('/auth/sessions'),

  revokeSession: (sessionId: string) =>
    apiClient.delete<{ success: boolean }>(`/auth/sessions/${sessionId}`),
};
