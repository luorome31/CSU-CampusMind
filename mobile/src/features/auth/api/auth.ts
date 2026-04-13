/**
 * 认证 API 调用
 */
import { api } from '../../../api/client';
import { LoginResponse } from '../../../types/api';

export const authApi = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),

  logout: () => api.post<{ message: string }>('/auth/logout'),
};
