import { renderHook, act } from '@testing-library/react-native';
import { useAuthStore } from '../authStore';

// Mock dependencies
jest.mock('../api/auth', () => ({
  authApi: {
    login: jest.fn(),
    logout: jest.fn(),
  },
}));

jest.mock('../../utils/storage', () => ({
  storage: {
    setToken: jest.fn(),
    setSessionId: jest.fn(),
    getToken: jest.fn(),
    getSessionId: jest.fn(),
    clear: jest.fn(),
  },
}));

jest.mock('../../api/client', () => ({
  setUnauthorizedCallback: jest.fn(),
}));

const { authApi } = require('../api/auth');
const { storage } = require('../../utils/storage');

describe('useAuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        user_id: '123',
        token: 'mock-token',
        session_id: 'mock-session',
      };
      authApi.login.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('student123', 'password');
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('mock-token');
      expect(result.current.user?.id).toBe('123');
      expect(storage.setToken).toHaveBeenCalledWith('mock-token');
      expect(storage.setSessionId).toHaveBeenCalledWith('mock-session');
    });

    it('should handle login failure', async () => {
      authApi.login.mockRejectedValue(new Error('Invalid credentials'));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        try {
          await result.current.login('student123', 'wrong');
        } catch (e) {
          // Expected
        }
      });

      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      authApi.logout.mockResolvedValue({ message: 'ok' });

      const { result } = renderHook(() => useAuthStore());

      // Setup logged in state
      await act(async () => {
        result.current.login('student123', 'password');
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(storage.clear).toHaveBeenCalled();
    });
  });

  describe('initAuth', () => {
    it('should restore session from storage', async () => {
      storage.getToken.mockResolvedValue('stored-token');
      storage.getSessionId.mockResolvedValue('stored-session');

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.initAuth();
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('stored-token');
    });

    it('should not authenticate without token', async () => {
      storage.getToken.mockResolvedValue(null);
      storage.getSessionId.mockResolvedValue(null);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.initAuth();
      });

      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});
