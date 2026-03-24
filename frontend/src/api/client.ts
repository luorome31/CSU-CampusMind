import { ApiError } from './types';

// Token helper reads directly from sessionStorage — avoids circular import with authStore
function getToken(): string | null {
  return sessionStorage.getItem('token');
}

function getSessionId(): string | null {
  return sessionStorage.getItem('sessionId');
}

class ApiClient {
  private baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = getToken();
    const sessionId = getSessionId();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(sessionId ? { 'X-Session-ID': sessionId } : {}),
        ...options.headers,
      },
    });

    if (response.status === 401) {
      // Clear session and reload to trigger auth re-init
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('sessionId');
      window.location.href = '/login';
      throw new ApiError(401, 'Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.detail || 'Request failed');
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) return {} as T;
    return JSON.parse(text) as T;
  }

  get<T>(url: string) {
    return this.request<T>(url, { method: 'GET' });
  }

  post<T>(url: string, data?: unknown) {
    return this.request<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  delete<T>(url: string) {
    return this.request<T>(url, { method: 'DELETE' });
  }

  patch<T>(url: string, data?: unknown) {
    return this.request<T>(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

export const apiClient = new ApiClient();
