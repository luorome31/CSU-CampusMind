/**
 * AuthStore - 认证状态管理
 */
import { create } from 'zustand';
import { authApi } from './api/auth';
import { storage } from '../../utils/storage';
import { setUnauthorizedCallback } from '../../api/client';
import type { User } from '../../types/api';

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
      const response = await authApi.login(username, password);
      const data = response.data;
      const user: User = {
        id: data.user_id,
        username,
      };
      const token = data.token;
      const sessionId = data.session_id;

      await storage.setToken(token);
      await storage.setSessionId(sessionId);

      set({ user, token, sessionId, isAuthenticated: true, isLoading: false });
    } catch (error) {
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
