/**
 * Profile API 模块
 */

import { apiClient } from '../../../api/client';
import type { User, UsageStats, Session } from '../../../types/user';

export interface UpdateProfileData {
  display_name?: string;
  email?: string;
  phone?: string;
}

export const profileApi = {
  getProfile: () => apiClient.get<User>('/users/me'),

  updateProfile: (data: UpdateProfileData) =>
    apiClient.patch<User>('/users/me', data),

  getStats: () => apiClient.get<UsageStats>('/users/me/stats'),

  getSessions: () => apiClient.get<Session[]>('/auth/sessions'),
};
