import { create } from 'zustand';
import { authApi } from '../../api/auth';
import { User } from '../../api/types';

interface AuthState {
  user: User | null;
  token: string | null;
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
  isAuthenticated: false,
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login(username, password);
      const user: User = { user_id: response.user_id, username };
      const token = response.token;

      sessionStorage.setItem('token', token);
      sessionStorage.setItem('user', JSON.stringify(user));

      set({ user, token, isAuthenticated: true, isLoading: false });
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
      set({ user: null, token: null, isAuthenticated: false });
    }
  },

  initAuth: async () => {
    const token = sessionStorage.getItem('token');
    const userStr = sessionStorage.getItem('user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        set({ user, token, isAuthenticated: true });
      } catch {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
      }
    }
  },
}));
