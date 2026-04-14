/**
 * API 客户端
 * Axios 实例 + token 注入 + 401 自动登出拦截器
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { storage } from '../utils/storage';
import { ApiError } from '../types/api';

// 401 回调机制
let onUnauthorizedCallback: (() => void) | null = null;

export const setUnauthorizedCallback = (callback: () => void) => {
  onUnauthorizedCallback = callback;
};

// 创建 Axios 实例
const createApiClient = () => {
  const client = axios.create({
    baseURL: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器：注入 token
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const token = await storage.getToken();
      const sessionId = await storage.getSessionId();

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      if (sessionId && config.headers) {
        config.headers['X-Session-ID'] = sessionId;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器：处理 401
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // 清除存储并触发登出
        await storage.clear();
        onUnauthorizedCallback?.();
        throw new ApiError(401, 'Unauthorized');
      }

      // 其他错误解析
      const errorDetail =
        (error.response?.data as { detail?: string })?.detail ||
        error.message ||
        'Request failed';
      throw new ApiError(error.response?.status || 500, errorDetail);
    }
  );

  return client;
};

export const apiClient = createApiClient();

// 便捷方法
export const api = {
  get: <T>(url: string) => apiClient.get<T>(url),
  post: <T>(url: string, data?: unknown) => apiClient.post<T>(url, data),
  delete: <T>(url: string) => apiClient.delete<T>(url),
  patch: <T>(url: string, data?: unknown) =>
    apiClient.patch<T>(url, data),
};
