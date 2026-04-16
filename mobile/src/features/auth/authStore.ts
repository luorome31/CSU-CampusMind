/**
 * AuthStore - 认证状态管理
 */
import { create } from 'zustand';
import { authApi } from './api/auth';
import { storage } from '../../utils/storage';
import { logger } from '../../utils/logger';
import { setUnauthorizedCallback } from '../../api/client';
import type { User } from '../../types/api';

const TAG = 'AuthStore';

interface AuthState {
  user: User | null;
  token: string | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  sessionId: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      logger.debug(TAG, '开始调用 authApi.login...');
      const response = await authApi.login(username, password);
      logger.debug(TAG, 'API返回响应状态:', response.status);
      
      const data = response.data;
      logger.debug(TAG, '解析到的响应数据:', data);

      const user: User = {
        id: data.user_id,
        username,
      };
      const token = data.token;
      const sessionId = data.session_id;

      logger.debug(TAG, '写入 token...');
      await storage.setToken(token);
      logger.debug(TAG, '写入 sessionId...');
      await storage.setSessionId(sessionId);

      logger.debug(TAG, '认证完成，更新 store 状态');
      set({ user, token, sessionId, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      logger.error(TAG, 'Login failed with error:', error?.message || error);
      if (error?.response) {
         logger.error(TAG, '响应详情:', error.response.data);
      }
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore logout errors — clear state anyway
    } finally {
      await storage.clear();
      set({ user: null, token: null, sessionId: null, isAuthenticated: false });
    }
  },

  initAuth: async () => {
    set({ isLoading: true });
    const token = await storage.getToken();
    const sessionId = await storage.getSessionId();

    if (token && sessionId) {
      // Restore session without server validation
      set({
        token,
        sessionId,
        isAuthenticated: true,
        isLoading: false,
      });
    } else {
      set({ isLoading: false });
    }
  },
}));

// Setup 401 callback
setUnauthorizedCallback(() => {
  useAuthStore.getState().logout();
});
