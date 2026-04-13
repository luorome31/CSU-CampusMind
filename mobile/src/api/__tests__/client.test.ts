/**
 * API Client Tests
 */

import { describe, it, expect, jest, beforeEach } from '@jest/globals';

describe('apiClient', () => {
  // Properly typed mock functions
  let mockRequestUse: jest.Mock;
  let mockResponseUse: jest.Mock;
  let mockGetToken: jest.Mock<() => Promise<string | null>>;
  let mockGetSessionId: jest.Mock<() => Promise<string | null>>;
  let mockClear: jest.Mock<() => Promise<void>>;
  let apiClient: any;
  let setUnauthorizedCallback: (callback: () => void) => void;

  beforeEach(() => {
    jest.resetModules();

    // Create fresh mock functions for each test
    mockRequestUse = jest.fn();
    mockResponseUse = jest.fn();
    mockGetToken = jest.fn();
    mockGetSessionId = jest.fn();
    mockClear = jest.fn();

    // Mock axios inline
    jest.doMock('axios', () => ({
      create: jest.fn(() => ({
        interceptors: {
          request: { use: mockRequestUse },
          response: { use: mockResponseUse },
        },
        get: jest.fn(),
        post: jest.fn(),
        delete: jest.fn(),
        patch: jest.fn(),
      })),
      AxiosError: class extends Error {
        response?: { status: number; data?: unknown };
        constructor(response?: { status: number; data?: unknown }, message?: string) {
          super(message);
          this.name = 'AxiosError';
          this.response = response;
        }
      },
    }));

    // Mock storage
    jest.doMock('../../utils/storage', () => ({
      storage: {
        getToken: mockGetToken,
        getSessionId: mockGetSessionId,
        clear: mockClear,
      },
    }));

    // Mock ApiError
    class MockApiError extends Error {
      status: number;
      detail: string;
      constructor(status: number, detail: string) {
        super(detail);
        this.name = 'ApiError';
        this.status = status;
        this.detail = detail;
      }
    }

    jest.doMock('../../types/api', () => ({
      ApiError: MockApiError,
    }));

    // Import after setting up mocks
    const clientModule = require('../client');
    apiClient = clientModule.apiClient;
    setUnauthorizedCallback = clientModule.setUnauthorizedCallback;
  });

  describe('token injection', () => {
    it('should inject token into request headers', async () => {
      mockGetToken.mockResolvedValue('test_token');
      mockGetSessionId.mockResolvedValue('test_session');

      // Get the request interceptor callback
      const requestCallback = mockRequestUse.mock.calls[0][0] as any;

      // Create a mock config
      const mockConfig = {
        headers: {} as Record<string, string>,
      };

      // Execute the interceptor
      await requestCallback(mockConfig);

      expect(mockConfig.headers['Authorization']).toBe('Bearer test_token');
      expect(mockConfig.headers['X-Session-ID']).toBe('test_session');
    });

    it('should not inject token if not present', async () => {
      mockGetToken.mockResolvedValue(null);
      mockGetSessionId.mockResolvedValue(null);

      const requestCallback = mockRequestUse.mock.calls[0][0] as any;

      const mockConfig = {
        headers: {} as Record<string, string>,
      };

      await requestCallback(mockConfig);

      expect(mockConfig.headers['Authorization']).toBeUndefined();
      expect(mockConfig.headers['X-Session-ID']).toBeUndefined();
    });
  });

  describe('401 handling', () => {
    it('should clear storage on 401 response', async () => {
      mockClear.mockResolvedValue(undefined);

      // Get the error callback (second argument to response.use)
      // response.use(fn1, fn2) means calls[0] = [fn1, fn2]
      const errorCallback = mockResponseUse.mock.calls[0][1] as any;

      // Create a mock 401 error
      const mockError = { response: { status: 401 } };

      try {
        await errorCallback(mockError);
      } catch (e) {
        // Expected to throw
      }

      expect(mockClear).toHaveBeenCalled();
    });

    it('should call onUnauthorizedCallback on 401', async () => {
      mockClear.mockResolvedValue(undefined);

      const errorCallback = mockResponseUse.mock.calls[0][1] as any;
      const mockError = { response: { status: 401 } };

      const callback = jest.fn();
      setUnauthorizedCallback(callback);

      try {
        await errorCallback(mockError);
      } catch (e) {
        // Expected to throw
      }

      expect(callback).toHaveBeenCalled();
    });

    it('should throw ApiError with 401 status on 401 response', async () => {
      mockClear.mockResolvedValue(undefined);

      const errorCallback = mockResponseUse.mock.calls[0][1] as any;
      const mockError = { response: { status: 401 } };

      let thrownError: any;
      try {
        await errorCallback(mockError);
      } catch (e) {
        thrownError = e;
      }

      expect(thrownError).toBeDefined();
      expect(thrownError.status).toBe(401);
      expect(thrownError.detail).toBe('Unauthorized');
    });
  });

  describe('error parsing', () => {
    it('should parse error detail from response data', async () => {
      const errorCallback = mockResponseUse.mock.calls[0][1] as any;

      const mockError = {
        response: {
          status: 400,
          data: { detail: 'Validation error' },
        },
      };

      let thrownError: any;
      try {
        await errorCallback(mockError);
      } catch (e) {
        thrownError = e;
      }

      expect(thrownError.status).toBe(400);
      expect(thrownError.detail).toBe('Validation error');
    });

    it('should use error message if no detail in response', async () => {
      const errorCallback = mockResponseUse.mock.calls[0][1] as any;

      const mockError = {
        response: { status: 500 },
        message: 'Network error',
      };

      let thrownError: any;
      try {
        await errorCallback(mockError);
      } catch (e) {
        thrownError = e;
      }

      expect(thrownError.status).toBe(500);
      expect(thrownError.detail).toBe('Network error');
    });

    it('should default to "Request failed" if no detail or message', async () => {
      const errorCallback = mockResponseUse.mock.calls[0][1] as any;

      // No response object - should default to 500
      const mockError = {};

      let thrownError: any;
      try {
        await errorCallback(mockError);
      } catch (e) {
        thrownError = e;
      }

      expect(thrownError.status).toBe(500);
      expect(thrownError.detail).toBe('Request failed');
    });
  });
});