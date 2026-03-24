import { create } from 'zustand';
import { authApi } from '../../api/auth';
import { User } from '../../api/types';

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

export const authStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  sessionId: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login(username, password);
      const user: User = { user_id: response.user_id, username };
      const token = response.token;
      const sessionId = response.session_id;

      sessionStorage.setItem('token', token);
      sessionStorage.setItem('user', JSON.stringify(user));
      sessionStorage.setItem('sessionId', sessionId);

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
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('sessionId');
      set({ user: null, token: null, sessionId: null, isAuthenticated: false });
    }
  },

  initAuth: async () => {
    const token = sessionStorage.getItem('token');
    const userStr = sessionStorage.getItem('user');
    const sessionId = sessionStorage.getItem('sessionId');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({ user, token, sessionId, isAuthenticated: true });
      } catch {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('sessionId');
      }
    }
  },
}));
