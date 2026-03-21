import { apiClient } from './client';
import { LoginResponse } from './types';

export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<LoginResponse>('/auth/login', { username, password }),

  logout: () => apiClient.post<{ message: string }>('/auth/logout'),

  refresh: () => apiClient.post<LoginResponse>('/auth/refresh'),
};
