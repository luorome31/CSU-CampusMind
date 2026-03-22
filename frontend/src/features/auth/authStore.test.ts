import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { authStore } from './authStore';
import * as authApi from '../../api/auth';

vi.mock('../../api/auth', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
}));

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    authStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    // Clear sessionStorage
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  describe('initial state', () => {
    it('has null user', () => {
      expect(authStore.getState().user).toBeNull();
    });

    it('has null token', () => {
      expect(authStore.getState().token).toBeNull();
    });

    it('is not authenticated', () => {
      expect(authStore.getState().isAuthenticated).toBe(false);
    });

    it('is not loading', () => {
      expect(authStore.getState().isLoading).toBe(false);
    });
  });

  describe('login', () => {
    it('sets isLoading to true during login', async () => {
      vi.mocked(authApi.authApi.login).mockResolvedValue({
        token: 'test-token',
        user_id: 'user-1',
        expires_in: 3600,
      });

      const loginPromise = authStore.getState().login('user', 'pass');
      expect(authStore.getState().isLoading).toBe(true);
      await loginPromise;
    });

    it('sets user, token, and isAuthenticated on successful login', async () => {
      vi.mocked(authApi.authApi.login).mockResolvedValue({
        token: 'test-token',
        user_id: 'user-1',
        expires_in: 3600,
      });

      await authStore.getState().login('user', 'pass');

      expect(authStore.getState().user).toEqual({
        user_id: 'user-1',
        username: 'user',
      });
      expect(authStore.getState().token).toBe('test-token');
      expect(authStore.getState().isAuthenticated).toBe(true);
      expect(authStore.getState().isLoading).toBe(false);
    });

    it('stores token in sessionStorage', async () => {
      vi.mocked(authApi.authApi.login).mockResolvedValue({
        token: 'test-token',
        user_id: 'user-1',
        expires_in: 3600,
      });

      await authStore.getState().login('user', 'pass');

      expect(sessionStorage.getItem('token')).toBe('test-token');
    });

    it('stores user in sessionStorage', async () => {
      vi.mocked(authApi.authApi.login).mockResolvedValue({
        token: 'test-token',
        user_id: 'user-1',
        expires_in: 3600,
      });

      await authStore.getState().login('user', 'pass');

      const storedUser = JSON.parse(sessionStorage.getItem('user')!);
      expect(storedUser).toEqual({
        user_id: 'user-1',
        username: 'user',
      });
    });

    it('resets isLoading on login failure', async () => {
      vi.mocked(authApi.authApi.login).mockRejectedValue(new Error('Invalid credentials'));

      await expect(authStore.getState().login('user', 'wrong')).rejects.toThrow();
      expect(authStore.getState().isLoading).toBe(false);
    });

    it('rethrows login error', async () => {
      vi.mocked(authApi.authApi.login).mockRejectedValue(new Error('Invalid credentials'));

      await expect(authStore.getState().login('user', 'wrong')).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    beforeEach(async () => {
      // Setup authenticated state first
      vi.mocked(authApi.authApi.login).mockResolvedValue({
        token: 'test-token',
        user_id: 'user-1',
        expires_in: 3600,
      });
      await authStore.getState().login('user', 'pass');
    });

    it('calls authApi.logout', async () => {
      await authStore.getState().logout();
      expect(authApi.authApi.logout).toHaveBeenCalled();
    });

    it('clears user state', async () => {
      await authStore.getState().logout();
      expect(authStore.getState().user).toBeNull();
    });

    it('clears token state', async () => {
      await authStore.getState().logout();
      expect(authStore.getState().token).toBeNull();
    });

    it('sets isAuthenticated to false', async () => {
      await authStore.getState().logout();
      expect(authStore.getState().isAuthenticated).toBe(false);
    });

    it('removes token from sessionStorage', async () => {
      await authStore.getState().logout();
      expect(sessionStorage.getItem('token')).toBeNull();
    });

    it('removes user from sessionStorage', async () => {
      await authStore.getState().logout();
      expect(sessionStorage.getItem('user')).toBeNull();
    });

    it('clears state even if logout API fails', async () => {
      vi.mocked(authApi.authApi.logout).mockRejectedValue(new Error('Network error'));

      await authStore.getState().logout();

      expect(authStore.getState().user).toBeNull();
      expect(authStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe('initAuth', () => {
    it('does nothing if no token in sessionStorage', async () => {
      await authStore.getState().initAuth();
      expect(authStore.getState().isAuthenticated).toBe(false);
    });

    it('restores auth state from sessionStorage', async () => {
      sessionStorage.setItem('token', 'stored-token');
      sessionStorage.setItem('user', JSON.stringify({ user_id: 'user-1', username: 'stored' }));

      await authStore.getState().initAuth();

      expect(authStore.getState().isAuthenticated).toBe(true);
      expect(authStore.getState().token).toBe('stored-token');
      expect(authStore.getState().user).toEqual({ user_id: 'user-1', username: 'stored' });
    });

    it('clears sessionStorage if user data is invalid', async () => {
      sessionStorage.setItem('token', 'stored-token');
      sessionStorage.setItem('user', 'invalid-json');

      await authStore.getState().initAuth();

      expect(authStore.getState().isAuthenticated).toBe(false);
      expect(sessionStorage.getItem('token')).toBeNull();
      expect(sessionStorage.getItem('user')).toBeNull();
    });

    it('clears sessionStorage if token is missing but user exists', async () => {
      sessionStorage.removeItem('token');
      sessionStorage.setItem('user', JSON.stringify({ user_id: 'user-1', username: 'stored' }));

      await authStore.getState().initAuth();

      expect(authStore.getState().isAuthenticated).toBe(false);
    });
  });
});
