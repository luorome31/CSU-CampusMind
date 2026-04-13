import { renderHook, act } from '@testing-library/react-native';
import { useAuthStore } from '../authStore';

// Mock dependencies
jest.mock('../api/auth', () => ({
  authApi: {
    login: jest.fn(),
    logout: jest.fn(),
  },
}));

jest.mock('../../../utils/storage', () => ({
  storage: {
    setToken: jest.fn(),
    setSessionId: jest.fn(),
    getToken: jest.fn(),
    getSessionId: jest.fn(),
    clear: jest.fn(),
  },
}));

jest.mock('../../../api/client', () => ({
  setUnauthorizedCallback: jest.fn(),
}));

const { authApi } = require('../api/auth');
const { storage } = require('../../../utils/storage');

describe('useAuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      sessionId: null,
      isAuthenticated: false,
      isLoading: false,
    });
    // Reset default mock implementations
    storage.getToken.mockResolvedValue(null);
    storage.getSessionId.mockResolvedValue(null);
    storage.setToken.mockResolvedValue(undefined);
    storage.setSessionId.mockResolvedValue(undefined);
    storage.clear.mockResolvedValue(undefined);
    authApi.logout.mockResolvedValue({ data: { message: 'ok' } });
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const mockData = {
        user_id: '123',
        token: 'mock-token',
        session_id: 'mock-session',
      };
      // axios.post returns AxiosResponse with { data: ... }
      authApi.login.mockResolvedValue({ data: mockData });

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
      // Setup logged in state
      const mockData = {
        user_id: '123',
        token: 'mock-token',
        session_id: 'mock-session',
      };
      authApi.login.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login('student123', 'password');
      });

      expect(result.current.isAuthenticated).toBe(true);

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
